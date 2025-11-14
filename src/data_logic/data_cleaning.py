




class DataCleaning:
    """
    utilities for cleaning data
    """
    def __init__(self):
        self.article_field_names = {
            "publisher": "source"
        }

    def correct_article_keys(self, article: dict or list, recurse=True) -> dict or list:
        if isinstance(article, list):
            assert recurse, "cannot recurse further than one level deep"
            return [self.correct_article_keys(x, recurse=False) for x in article]
        else:
            assert isinstance(article, dict), "article must be a dict or list of dicts"
            return {self.article_field_names.get(k, k): v for k, v in article.items()}
