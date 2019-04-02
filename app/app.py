from flask import Flask, request, render_template
import PlottingAPI
import DatabaseAPI
import ProductSearch

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    category_list = DatabaseAPI.get_categories()
    if request.method == "POST":
        # Load selected category from form and replace the default value with None
        category = request.form.get("CategorySelector")
        if category.strip() == "AllCategories":
            category = None
        items = DatabaseAPI.get_items(category=category)

        # Load search string and perform search if necessary
        search = request.form.get("SearchString")
        if len(search.strip()) > 0:
            thresh = int(request.form.get("SearchThresh"))
            items_search = ProductSearch.search_similar(query=search, items=items, return_threshold=thresh/100)
            if len(items_search) == 0:
                items_search = None
                plot = None
            else:
                items_search["similarity_to_query"] *= 100
                items_search["similarity_to_query"] = items_search["similarity_to_query"].astype(int).astype(str)
                plot = PlottingAPI.make_price_boxplot(items=items_search)
                items_search = items_search.iloc[0:100].to_dict('records')
            return render_template(
                'index.html', category_list=category_list,
                category=category, item_list=items_search,
                byte_string=plot, query_string=search, query_thresh=thresh)
        else:
            plot = PlottingAPI.make_price_boxplot(items=items)
            return render_template(
                'index.html', category_list=category_list,
                category=category, byte_string=plot,
                item_list=None)

    # On default load without first submission
    else:
        items = DatabaseAPI.get_items(category=None)
        plot = PlottingAPI.make_price_boxplot(items=items)
        return render_template(
            'index.html', category_list=category_list,
            category=None, byte_string=plot)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
