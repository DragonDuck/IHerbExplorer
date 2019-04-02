import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


def make_price_boxplot(items, logscale=False):
    """
    Create a boxplot of price distributions.

    The grouping of the boxplot depnds on the 'category' column of 'items'. These values are of the form
    'super-category,subcategory'. If multiple super-categories exist, then these are the grouping factor. If only
    one super-category is present in the dataset, subcategories are used instead.

    :param items: Items to plot
    :param logscale: A boolean indicating whether to plot the price scale logarithmically:
    :return: A base64 string that can be embedded directly into an HTML page
    """
    items = items.copy()
    catsplit = items["category"].str.split(",", expand=True)
    items["supercategory"] = catsplit[0]
    items["subcategory"] = catsplit[1]

    if items["category"].nunique() > 1:
        g = sns.catplot(data=items, y="supercategory", x="price", kind="box", color="skyblue")
    else:
        g = sns.catplot(data=items, y="subcategory", x="price", kind="box", color="skyblue")
    g.set_axis_labels(y_var="Category", x_var="Price")
    if logscale:
        g.fig.get_axes()[0].set_xscale("log")
    plt.tight_layout(pad=1, w_pad=1, h_pad=1.0)
    bytes_image = io.BytesIO()
    g.savefig(bytes_image, format="png")
    bytes_image.seek(0)
    base64string = "data:image/png;base64," + base64.b64encode(bytes_image.getvalue()).decode("utf-8")
    plt.close()
    return base64string
