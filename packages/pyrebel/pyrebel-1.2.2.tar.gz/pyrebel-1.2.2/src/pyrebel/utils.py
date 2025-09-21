# Copyright (C) 2024-2025 Nithin PS.
# This file is part of Pyrebel.
#
# Pyrebel is free software: you can redistribute it and/or modify it under the terms of 
# the GNU General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
#
# Pyrebel is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Pyrebel.
# If not, see <https://www.gnu.org/licenses/>.
#

from numba import cuda
from math import sqrt
import numpy as np

def draw_pixels_cuda(pixels,i,img):        
    """Draws 'pixels' in 'img' with 'i'"""
    
    draw_pixels_cuda_[pixels.shape[0],1](pixels,i,img)
    cuda.synchronize()

@cuda.jit
def draw_pixels_cuda_(pixels,i,img):
    """Draws 'pixels' in 'img' with 'i'"""
    
    cc=cuda.grid(1)
    if cc<pixels.shape[0]:
        r=int(pixels[cc]/img.shape[1])
        c=pixels[cc]%img.shape[1]
        img[r][c]=i

@cuda.jit
def increment_by_one(array_d):
    """Increments each item in array 'array_d' by one."""
    
    ci=cuda.grid(1)
    if ci<len(array_d):
        array_d[ci]+=1
        cuda.syncthreads()

@cuda.jit
def decrement_by_one(array_d):
    """Decrements each item in array 'array_d' by one."""
    
    ci=cuda.grid(1)
    if ci<len(array_d):
        array_d[ci]-=1
        cuda.syncthreads()
        
def decrement_by_one_cuda(array):
    """Decrements each item in 'array' by one."""
    
    array_d=cuda.to_device(array)
    decrement_by_one[len(array),1](array_d)
    cuda.synchronize()
    return array_d.copy_to_host()    

def draw_pixels_from_indices_cuda(indices,pixels,i,img):
    """Draws 'indices' in 'pixels' in 'img' with 'i'."""
    
    draw_pixels_from_indices_cuda_[indices.shape[0],1](indices,pixels,i,img)
    cuda.synchronize()

@cuda.jit
def draw_pixels_from_indices_cuda_(indices,pixels,i,img):
    """Draws 'indices' in 'pixels' in 'img' with 'i'."""
    
    cc=cuda.grid(1)
    if cc<len(indices):
        r=int(pixels[indices[cc]]/img.shape[1])
        c=pixels[indices[cc]]%img.shape[1]
        img[r][c]=i
        
@cuda.jit
def image_to_wave(img_array_d,img_wave_pre_init_d):
    """Plot each row of 'img_array_d' in 2D space with color of pixels as y-coordinate."""
    
    r,c=cuda.grid(2)
    if r<img_array_d.shape[0] and c<img_array_d.shape[1]:
        img_wave_pre_init_d[r*img_array_d.shape[1]+c]=img_array_d[r][c]*img_array_d.shape[1]+c

@cuda.jit
def init_abstract(img_array_d,bound_abstract_pre_d):
    """Finds initial abstract points for each row in the input image. Each row is considered as separate boundary / blob."""
    
    ci=cuda.grid(1)
    if ci==0:
        bound_abstract_pre_d[ci]=ci+1
    elif ci<len(bound_abstract_pre_d) and ci%img_array_d.shape[1]==0:
        bound_abstract_pre_d[ci]=ci+1
        bound_abstract_pre_d[ci-1]=ci
    elif ci==len(bound_abstract_pre_d)-1:
        bound_abstract_pre_d[ci]=ci+1

@cuda.jit
def init_abstract_from_size(size_d,size_cum_d,init_abstract_d):
    ci=cuda.grid(1)
    if ci==0:
        init_abstract_d[0]=1
    elif ci>0 and ci<len(size_d):
        init_abstract_d[size_cum_d[ci]]=size_cum_d[ci]+1
        init_abstract_d[size_cum_d[ci]-1]=size_cum_d[ci]
    else:
        init_abstract_d[size_cum_d[len(size_d)-1]+size_d[len(size_d)-1]-1]=size_cum_d[len(size_d)-1]+size_d[len(size_d)-1]

@cuda.jit
def image_rotate45(img_array_d,img_rot45_d,img_rot45_mask_d):
    """Rotates an image by 45 degrees."""
    
    r,c=cuda.grid(2)
    if r<img_array_d.shape[0] and c<img_array_d.shape[1]:
        if r+c<img_array_d.shape[0]:
            img_rot45_d[r+c][c]=img_array_d[r][c]
            img_rot45_mask_d[r+c][c]=-1
        else:
            img_rot45_d[r+c][c-(r+c-img_array_d.shape[0])-1]=img_array_d[r][c]
            img_rot45_mask_d[r+c][c-(r+c-img_array_d.shape[0])-1]=-1

@cuda.jit
def image_rev_rotate45(img_rot45_d,img_rot45_mask_d,img_array_d):
    """Recovers the original image from image rotated by 45 degrees."""
    
    r,c=cuda.grid(2)
    if r<img_rot45_d.shape[0] and c<img_rot45_d.shape[1] and img_rot45_mask_d[r][c]!=-500:
        if r<img_array_d.shape[0]:
            img_array_d[r-c,c]=img_rot45_d[r][c]
        else:
            img_array_d[r-(r-(img_array_d.shape[0]-1))-c,r-(img_array_d.shape[0]-1)+c]=img_rot45_d[r][c]

@cuda.jit
def fill_column_zero(img_array_d):
    r,c=cuda.grid(2)
    if r<img_array_d.shape[0] and c<img_array_d.shape[1]:
        img_array_d[r][c]=img_array_d[r][0]

def draw_pixels_cuda2(pixels,exclusions,invert,i,img):
    """Draws 'pixels' in image 'img' with 'exclusions' with color 'i'"""
    
    draw_pixels_cuda2_[pixels.shape[0],1](pixels,exclusions,invert,i,img)
    cuda.synchronize()

@cuda.jit
def draw_pixels_cuda2_(pixels,exclusions,invert,i,img):
    """Draws 'pixels' in image 'img' with 'exclusions' with color 'i'"""
    
    cc=cuda.grid(1)
    if cc<pixels.shape[0]:
        if invert:
            if exclusions[cc]<0:
                r=int(pixels[cc]/img.shape[1])
                c=pixels[cc]%img.shape[1]
                img[r][c]=i
        else:
            if exclusions[cc]>0:
                r=int(pixels[cc]/img.shape[1])
                c=pixels[cc]%img.shape[1]
                img[r][c]=i
 
@cuda.jit
def clone_image(img_array,img_clone,color):
    """Draws pixels in 'img_array' with color 'color' to 'img_clone'"""
    
    r,c=cuda.grid(2)
    if r<img_array.shape[0] and c<img_array.shape[1]:
        if img_array[r][c]==color:
            img_clone[r][c]=color

@cuda.jit
def clone_image2(img_array_orig,image_to_clone,img_cloned,inv):
    """Draws pixels in 'image_to_clone' with color '255' to 'img_cloned' with the color of corresponding pixels in 'img_array_orig'"""
    
    r,c=cuda.grid(2)
    if r>0 and r<img_array_orig.shape[0] and c>0 and c<img_array_orig.shape[1]:
        if image_to_clone[r][c]==255:
            if inv:
                img_cloned[r][c]=img_array_orig[r][c]
            else:
                img_cloned[r][c]=255-img_array_orig[r][c]
            #cuda.atomic.add(count,0,1)
  
@cuda.jit
def clean_quant_img(quant_img_d):
    r,c=cuda.grid(2)
    if r>0 and r<quant_img_d.shape[0]-1 and c>0 and c<quant_img_d.shape[1]-1:
        if quant_img_d[r][c]!=0 and quant_img_d[r-1][c-1]==0 and quant_img_d[r-1][c]==0 and quant_img_d[r-1][c+1]==0 and quant_img_d[r][c-1]==0 and quant_img_d[r][c+1]==0 and quant_img_d[r+1][c-1]==0 and quant_img_d[r+1][c]==0 and quant_img_d[r+1][c+1]==0:
            quant_img_d[r][c]=0
                      
@cuda.jit
def draw_lines_neighbors_all(img_array_d,neighbor_img_d,color,threshold):
    r,c=cuda.grid(2)
    if r>threshold and r<img_array_d.shape[0]-threshold and c>threshold and c<img_array_d.shape[1]-threshold and img_array_d[r][c]!=0:
        for rrr in range(r-threshold,r+threshold):
            for ccc in range(c-threshold,c+threshold):
                cur_dist=sqrt(pow(r-rrr,2)+pow(c-ccc,2))
                if img_array_d[r][c]==img_array_d[rrr][ccc] and cur_dist<threshold:
                    x=c
                    y=r
                    cc=ccc
                    rr=rrr
                    dx=abs(x-cc)
                    dy=abs(y-rr)
                    sx=1 if cc<x else -1
                    sy=1 if rr<y else -1
                    err=dx-dy
                    while True:
                        neighbor_img_d[rr][cc]=img_array_d[r][c]
                        if cc==x and rr==y:
                            break
                        e2=2*err
                        if e2>-dy:
                            err-=dy
                            cc+=sx
                        elif e2<dx:
                            err+=dx
                            rr+=sy

@cuda.jit
def winding_number_kernel(polygon,bound_data_ordered_d,img_array_d,winding_out_img_d):
    """Flood fill 'polygon'"""
    
    py,px = cuda.grid(2)
    if py<winding_out_img_d.shape[0] and px<winding_out_img_d.shape[1]:
        winding_number = 0
        
        for i in range(polygon.shape[0]):
            p1=bound_data_ordered_d[polygon[i]]
            x1=p1%winding_out_img_d.shape[1]
            y1=int(p1/winding_out_img_d.shape[1])
            p2=bound_data_ordered_d[polygon[(i + 1) % polygon.shape[0]]]  # Next vertex (wraps around)
            x2=p2%winding_out_img_d.shape[1]
            y2=int(p2/winding_out_img_d.shape[1])

            if y1 <= py:
                if y2 > py:  # Upward crossing
                    if (x2 - x1) * (py - y1) - (px - x1) * (y2 - y1) > 0:
                        winding_number += 1
            else:
                if y2 <= py:  # Downward crossing
                    if (x2 - x1) * (py - y1) - (px - x1) * (y2 - y1) < 0:
                        winding_number -= 1

        if winding_number:
            winding_out_img_d[py][px]=img_array_d[y1][x1]
        #results[idx] = winding_number != 0  # Inside if winding number is non-zero


@cuda.jit
def draw_lines(nz_ba_d,nz_ba_size_d,bound_data_ordered_d,bound_mark_d,out_image_d,color,min_size):
    """Draw lines between abstract pixels."""
    
    ci=cuda.grid(1)
    if ci<len(nz_ba_d)-1:
        if (nz_ba_d[ci]+1)==nz_ba_d[ci+1] or nz_ba_size_d[bound_mark_d[nz_ba_d[ci]]]<min_size+1:
            return
        a=bound_data_ordered_d[nz_ba_d[ci]]
        b=bound_data_ordered_d[nz_ba_d[ci+1]]
        a1=int(a/out_image_d.shape[1])
        a2=a%out_image_d.shape[1]
        b1=int(b/out_image_d.shape[1])
        b2=b%out_image_d.shape[1]

        x=a2
        y=a1
        cc=b2
        rr=b1

        dx=abs(x-cc)
        dy=abs(y-rr)
        sx=1 if cc<x else -1
        sy=1 if rr<y else -1
        err=dx-dy
        while True:
            out_image_d[rr][cc]=color
            if cc==x and rr==y:
                break
            e2=2*err
            if e2>-dy:
                err-=dy
                cc+=sx
            elif e2<dx:
                err+=dx
                rr+=sy

@cuda.jit
def quantize_img(img_array_d,img_quantized_d,quant_size):
    r,c=cuda.grid(2)
    #quant_size=int(256/ncolors)
    if r<img_array_d.shape[0] and c<img_array_d.shape[1]:
        color=img_array_d[r][c]
        color_quant=int(round(color/quant_size))*quant_size
        img_quantized_d[r][c]=color_quant

@cuda.jit
def scale_down_pixels(orig_pixels_d,pixels_d,orig_shape_d,shape_d,scale_d):
    """Scale down the pixels 'orig_pixels' by 'scale_d'."""
    
    ci=cuda.grid(1)
    if ci<len(pixels_d):
        r_orig=int(orig_pixels_d[ci]/orig_shape_d[1])
        c_orig=orig_pixels_d[ci]%orig_shape_d[1]
        r=int(r_orig/scale_d)
        c=int(c_orig/scale_d)
        pixels_d[ci]=r*shape_d[1]+c

@cuda.jit
def draw_blocks(orig_img_array_d,img_array_d,block_img_d,width):
    """Paints the output of edge detection. Squares of width 'width' with a single color are painted with
    the average of the area in the original image."""
    
    r,c=cuda.grid(2)
    count=0
    if r<img_array_d.shape[0]-width+1 and c<img_array_d.shape[1]-width+1:
        area=0
        sum_r=0
        sum_g=0
        sum_b=0
        orig_color=img_array_d[r][c]
        for rr in range(r,r+width):
            for cc in range(c,c+width):
                area+=1
                if img_array_d[rr][cc]==orig_color:
                    count+=1
        if count==area:
            for rr in range(r,r+width):
                for cc in range(c,c+width):
                    sum_r+=orig_img_array_d[rr][cc][0]
                    sum_g+=orig_img_array_d[rr][cc][1]
                    sum_b+=orig_img_array_d[rr][cc][2]
            for rr in range(r,r+width):
                for cc in range(c,c+width):
                    block_img_d[rr][cc][0]=int(sum_r/(width**2))
                    block_img_d[rr][cc][1]=int(sum_g/(width**2))
                    block_img_d[rr][cc][2]=int(sum_b/(width**2))
                    
def run_cuda_duplicate_detection_large(arr):
    """Marks duplicates in 3D array along axis-1"""
    
    assert arr.ndim == 3, "Input must be a 3D array"
    a, b, c = arr.shape  # shape: (batches, rows, cols)

    # Allocate device memory
    arr_device = cuda.to_device(arr)
    dup_mask=np.zeros((a,b),dtype=np.bool_)
    dup_mask_device=cuda.to_device(dup_mask)
    #dup_mask_device = cuda.device_array((a, b), dtype=np.bool_)

    # Define thread block and grid sizes
    threads_per_block = (16, 16)
    blocks_per_grid_x = (a + threads_per_block[0] - 1) // threads_per_block[0]
    blocks_per_grid_y = (b + threads_per_block[1] - 1) // threads_per_block[1]
    blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y)

    # Launch kernel
    mark_duplicates_cuda_large[blocks_per_grid, threads_per_block](arr_device, dup_mask_device)
    cuda.synchronize()
    # Copy result back
    return dup_mask_device.copy_to_host()
                    
@cuda.jit
def mark_duplicates_cuda_large(arr, dup_mask):
    """CUDA Kernel to mark duplicates in 3D array along axis-1"""
    
    batch_idx = cuda.blockIdx.x * cuda.blockDim.x + cuda.threadIdx.x
    row_idx = cuda.blockIdx.y * cuda.blockDim.y + cuda.threadIdx.y

    num_batches = arr.shape[0]
    num_rows = arr.shape[1]
    num_cols = arr.shape[2]

    if batch_idx >= num_batches or row_idx >= num_rows:
        return

    # Compare this row against all previous rows in the same batch
    for other_row in range(row_idx):
        is_duplicate = True
        for col in range(num_cols):
            if arr[batch_idx, row_idx, col] != arr[batch_idx, other_row, col]:
                is_duplicate = False
                break
        if is_duplicate:
            dup_mask[batch_idx, row_idx] = True
            return  # Found duplicate, exit early

@cuda.jit
def fill_axis1(array_d,mask_d,val):
    """CUDA Kernel to fill 3D array with 2D mask array with a scalar along axis-2"""
    
    r,c=cuda.grid(2)
    if r<array_d.shape[0] and c<array_d.shape[1]:
        if mask_d[r][c]:
            for index in range(array_d.shape[2]):
                array_d[r][c][index]=val

@cuda.jit
def get_row_wise_count(mask_d,count_d):
    r,c=cuda.grid(2)
    if r<mask_d.shape[0] and c<mask_d.shape[1]:
        if not mask_d[r][c]:
            cuda.atomic.add(count_d,r,1)

@cuda.jit
def is_blob_inside(bound_size_i_d,bound_size_i_cum_d,bound_data_d,bound_seed_d,shape_d,is_inside_d):
    idx,idy=cuda.grid(2)
    if idx<len(bound_size_i_d) and idy<len(bound_size_i_d) and idx!=idy and idx>1 and idy>1:
        polygon_len=bound_size_i_d[idx]    
            
        ii=bound_seed_d[idy] 
        x=int(ii/shape_d[1])
        y=ii%shape_d[1]       


        inside = False
        j = polygon_len - 1

        for i in range(polygon_len):
            ii=bound_data_d[bound_size_i_cum_d[idx]+i]
            xi=int(ii/shape_d[1])
            yi=ii%shape_d[1]
            jj=bound_data_d[bound_size_i_cum_d[idx]+j]
            xj=int(jj/shape_d[1])
            yj=jj%shape_d[1]
            

            # Check if the ray crosses the edge
            intersect = ((yi > y) != (yj > y)) and \
                        (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi)
            if intersect:
                inside = not inside
            j = i
        
        if inside:
            cuda.atomic.add(is_inside_d,idy,1)
                
