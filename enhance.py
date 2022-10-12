import cv2
from matplotlib import pyplot as plt

if __name__ == "__main__":
    image = cv2.imread("in.jpg")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = [float(hist[0])]
    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent = 1
    clip_hist_percent *= maximum / 100.0
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size - 1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    # Calculate new histogram with desired range and show histogram
    new_hist = cv2.calcHist([gray], [0], None, [256], [minimum_gray, maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0, 256])
    plt.show()

    result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    cv2.imwrite("out.jpg", img=result)
