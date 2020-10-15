from haystack import indexes
from .models import School, Tag


class SchoolIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True,
        template_name='search_indexes/school_text.html')
    text_auto = indexes.EdgeNgramField(use_template=True,
        template_name='search_indexes/school_text.html')

    continent = indexes.CharField(model_attr='country__continent')
    country = indexes.CharField(model_attr='country__name')
    tags = indexes.MultiValueField()

    name_auto = indexes.NgramField(model_attr='name')

    def get_model(self):
        return School

    def prepare_tags(self, obj):
        return [tag.id for tag in obj.tags.all()]

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(page__archived=False)


class TagIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True)
    name_auto = indexes.NgramField(model_attr='name')

    def get_model(self):
        return Tag
