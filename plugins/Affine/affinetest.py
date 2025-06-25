import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

# Path to your image and mask
img_path = r"plugins/Affine/testImages/NC1.png"  # Change as needed
mask_path = r"plugins/Affine/masks/refLED_v3_flat.png"

# Load image and mask
img = cv.imread(img_path)
mask = cv.imread(mask_path)
if img is None or mask is None:
    raise FileNotFoundError(f"Could not load image or mask from {img_path} or {mask_path}")
img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
mask = cv.cvtColor(mask, cv.COLOR_BGR2RGB)

# blur images
img = cv.GaussianBlur(img, (5, 5), 0)  # Optional: blur image for better feature extraction
mask = cv.GaussianBlur(mask, (5, 5), 0)  # Optional: blur mask for better feature extraction

# Convert to grayscale
gray_img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
gray_mask = cv.cvtColor(mask, cv.COLOR_RGB2GRAY)
gray_mask = cv.GaussianBlur(gray_mask, (5, 5), 0)  # Optional: blur mask for better feature extraction


# --- MARKER-BASED REGISTRATION WITH RECTANGLE SELECTION ---
print("\n--- Marker-based registration with rectangle selection ---")

# 1. User draws rectangle on mask to select marker region
plt.figure(figsize=(8, 8))
plt.title("Draw rectangle on MASK to select marker region")
plt.imshow(mask)
plt.axis("off")
rect_mask = plt.ginput(2, timeout=-1)
plt.close()
print(f"Mask rectangle: {rect_mask}")

# Extract rectangle coordinates
(x0m, y0m), (x1m, y1m) = rect_mask
x0m, x1m = int(round(x0m)), int(round(x1m))
y0m, y1m = int(round(y0m)), int(round(y1m))
x0m, x1m = min(x0m, x1m), max(x0m, x1m)
y0m, y1m = min(y0m, y1m), max(y0m, y1m)

# Show selected region
plt.figure(figsize=(8, 8))
plt.title("Selected region on MASK")
plt.imshow(mask)
plt.gca().add_patch(plt.Rectangle((x0m, y0m), x1m - x0m, y1m - y0m, edgecolor="red", facecolor="none", lw=2))
plt.axis("off")
plt.show()

# 2. Extract template from the selected mask rectangle (rectangular, not square)
template_mask = gray_mask[y0m:y1m, x0m:x1m]

plt.figure(figsize=(4, 4))
plt.title("Template from MASK (rectangular)")
plt.imshow(template_mask, cmap="gray")
plt.axis("off")
plt.show()

# 3. Template match to find all markers in mask
result_mask = cv.matchTemplate(gray_mask, template_mask, cv.TM_CCOEFF_NORMED)
locs_mask = np.where(result_mask > 0.7)
mask_markers = list(zip(locs_mask[1] + (x1m - x0m) // 2, locs_mask[0] + (y1m - y0m) // 2))


# Remove duplicates (close points)
def filter_close(points, min_dist):
    filtered = []
    for pt in points:
        if all(np.linalg.norm(np.array(pt) - np.array(f)) > min_dist for f in filtered):
            filtered.append(pt)
    return filtered


mask_markers = filter_close(mask_markers, min((x1m - x0m) // 2, (y1m - y0m) // 2))
# Sort so that the first marker is always the top-left
mask_markers = sorted(mask_markers, key=lambda x: (x[1], x[0]))
print(f"Found {len(mask_markers)} markers in mask. Top-left marker: {mask_markers[0] if mask_markers else None}")

plt.figure(figsize=(8, 8))
plt.title("Detected markers in MASK (top-left highlighted)")
plt.imshow(mask)
if mask_markers:
    plt.scatter(*zip(*mask_markers), c="red", marker="o", label="All markers")
    plt.scatter(*mask_markers[0], c="yellow", marker="*", s=200, label="Top-left marker")
    plt.legend()
plt.axis("off")
plt.show()

# 4. User draws rectangle on image to select marker region
plt.figure(figsize=(8, 8))
plt.title("Draw rectangle on IMAGE to select marker region")
plt.imshow(img)
plt.axis("off")
rect_img = plt.ginput(2, timeout=-1)
plt.close()
print(f"Image rectangle: {rect_img}")

(x0i, y0i), (x1i, y1i) = rect_img
x0i, x1i = int(round(x0i)), int(round(x1i))
y0i, y1i = int(round(y0i)), int(round(y1i))
x0i, x1i = min(x0i, x1i), max(x0i, x1i)
y0i, y1i = min(y0i, y1i), max(y0i, y1i)

plt.figure(figsize=(8, 8))
plt.title("Selected region on IMAGE")
plt.imshow(img)
plt.gca().add_patch(plt.Rectangle((x0i, y0i), x1i - x0i, y1i - y0i, edgecolor="blue", facecolor="none", lw=2))
plt.axis("off")
plt.show()

# 5. Extract template from the selected image rectangle (rectangular, not square)
template_img = gray_img[y0i:y1i, x0i:x1i]

plt.figure(figsize=(4, 4))
plt.title("Template from IMAGE (rectangular)")
plt.imshow(template_img, cmap="gray")
plt.axis("off")
plt.show()

# 6. Template match to find all markers in image
result_img = cv.matchTemplate(gray_img, template_img, cv.TM_CCOEFF_NORMED)
locs_img = np.where(result_img > 0.7)
img_markers = list(zip(locs_img[1] + (x1i - x0i) // 2, locs_img[0] + (y1i - y0i) // 2))
img_markers = filter_close(img_markers, min((x1i - x0i) // 2, (y1i - y0i) // 2))
# Sort so that the first marker is always the top-left
img_markers = sorted(img_markers, key=lambda x: (x[1], x[0]))
print(f"Found {len(img_markers)} markers in image. Top-left marker: {img_markers[0] if img_markers else None}")

plt.figure(figsize=(8, 8))
plt.title("Detected markers in IMAGE (top-left highlighted)")
plt.imshow(img)
if img_markers:
    plt.scatter(*zip(*img_markers), c="blue", marker="o", label="All markers")
    plt.scatter(*img_markers[0], c="yellow", marker="*", s=200, label="Top-left marker")
    plt.legend()
plt.axis("off")
plt.show()

# 7. Pair markers by sorting (row, then col)
if len(mask_markers) >= 3 and len(img_markers) >= 3:
    mask_sorted = sorted(mask_markers, key=lambda x: (x[1], x[0]))
    img_sorted = sorted(img_markers, key=lambda x: (x[1], x[0]))
    num_pairs = min(len(mask_sorted), len(img_sorted))
    src = np.float32(mask_sorted[:num_pairs])
    dst = np.float32(img_sorted[:num_pairs])
    # 8. Compute affine transform
    M, inliers = cv.estimateAffine2D(src, dst, method=cv.RANSAC, ransacReprojThreshold=5.0)
    print(f"Affine matrix:\n{M}")
    # 9. Visualize registration
    mask_warped = cv.warpAffine(mask, M, (img.shape[1], img.shape[0]))
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.title("Markers: Image (blue), Mask (red)")
    plt.imshow(img)
    plt.scatter(*zip(*img_sorted), c="blue", marker="o", label="Image markers")
    plt.scatter(*zip(*mask_sorted), c="red", marker="x", label="Mask markers")
    plt.legend()
    plt.axis("off")
    plt.subplot(1, 2, 2)
    plt.title("Mask warped to image")
    plt.imshow(img, alpha=0.7)
    plt.imshow(mask_warped, alpha=0.3)
    plt.axis("off")
    plt.tight_layout()
    plt.show()
else:
    print("Not enough markers found in both images for affine transform.")
