import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def display_images(image_list=None, title=None, bboxes_list=None):
    if image_list is None:
        image_list = []
    
    if title is None:
        title = ""
    
    if bboxes_list is None:
        bboxes_list = []
    
    #(False, True)
    if not any(isinstance(i, list) for i in image_list):
        image_list = [image_list] #[img, img, img] => [[img, img, img]]

    rows = len(image_list)
    cols = max(len(row) if isinstance(row , list) else 1 for row in image_list)

    plt.suptitle(title)
    fig, ax = plt.subplots(rows, cols)

    #确保ax是2D数组
    #ax => [[ax]], [ax]=>[[ax]]
    ax = np.atleast_2d(ax)

    for i, row in enumerate(image_list):
        if not isinstance(row, list):
            row = [row]
        
        for j, img in enumerate(row):
            ax[i, j].imshow(img)
            ax[i, j].axis("off")

            bbox_index = i * cols + j
            if bbox_index < len(bboxes_list):
                for bbox in bboxes_list[bbox_index]:
                    x_min, y_min, x_max, y_max = bbox
                    width = x_max - x_min
                    height = y_max - y_min
                    rect = patches.Rectangle(
                        (x_min, y_min),
                        width,
                        height,
                        linewidth=2,
                        edgecolor="r",
                        facecolor="none"
                    )
                    ax[i, j].add_patch(rect)

        for j in range(len(row), cols):
            ax[i, j].axis("off")

    #plt.tight_layout()
    plt.show()