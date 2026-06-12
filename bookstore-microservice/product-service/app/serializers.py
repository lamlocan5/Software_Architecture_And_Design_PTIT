from rest_framework import serializers
from .models import Product, Publisher, Category

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    author = serializers.CharField(write_only=True, required=False, allow_blank=True)
    publisher = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    product_type = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'stock', 'author', 'publisher', 'product_type']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['author'] = instance.attributes.get('author', '')
        pub_id = instance.attributes.get('publisher_id')
        ret['publisher'] = pub_id
        if pub_id:
            try:
                publisher = Publisher.objects.get(id=pub_id)
                ret['publisher_detail'] = PublisherSerializer(publisher).data
            except Publisher.DoesNotExist:
                ret['publisher_detail'] = None
        else:
            ret['publisher_detail'] = None
        return ret

    def create(self, validated_data):
        author = validated_data.pop('author', '')
        publisher = validated_data.pop('publisher', None)
        name = validated_data.pop('name', '')
        attributes = {
            'author': author,
            'publisher_id': publisher
        }
        product = Product.objects.create(
            name=name,
            product_type='book',
            attributes=attributes,
            **validated_data
        )
        return product

    def update(self, instance, validated_data):
        author = validated_data.pop('author', None)
        publisher = validated_data.pop('publisher', None)
        if author is not None:
            instance.attributes['author'] = author
        if publisher is not None:
            instance.attributes['publisher_id'] = publisher
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.save()
        return instance

class ClothingSerializer(serializers.ModelSerializer):
    size = serializers.CharField(write_only=True, required=False, allow_blank=True)
    color = serializers.CharField(write_only=True, required=False, allow_blank=True)
    category = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    product_type = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'size', 'color', 'category', 'product_type']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['size'] = instance.attributes.get('size', '')
        ret['color'] = instance.attributes.get('color', '')
        cat_id = instance.attributes.get('category_id')
        ret['category'] = cat_id
        if cat_id:
            try:
                category = Category.objects.get(id=cat_id)
                ret['category_detail'] = CategorySerializer(category).data
            except Category.DoesNotExist:
                ret['category_detail'] = None
        else:
            ret['category_detail'] = None
        return ret

    def create(self, validated_data):
        size = validated_data.pop('size', '')
        color = validated_data.pop('color', '')
        category = validated_data.pop('category', None)
        name = validated_data.pop('name', '')
        attributes = {
            'size': size,
            'color': color,
            'category_id': category
        }
        product = Product.objects.create(
            name=name,
            product_type='clothing',
            attributes=attributes,
            **validated_data
        )
        return product

    def update(self, instance, validated_data):
        size = validated_data.pop('size', None)
        color = validated_data.pop('color', None)
        category = validated_data.pop('category', None)
        if size is not None:
            instance.attributes['size'] = size
        if color is not None:
            instance.attributes['color'] = color
        if category is not None:
            instance.attributes['category_id'] = category
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.save()
        return instance

class ElectronicSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(write_only=True, required=False, allow_blank=True)
    model = serializers.CharField(write_only=True, required=False, allow_blank=True)
    category = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    product_type = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'brand', 'model', 'category', 'product_type']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['brand'] = instance.attributes.get('brand', '')
        ret['model'] = instance.attributes.get('model', '')
        cat_id = instance.attributes.get('category_id')
        ret['category'] = cat_id
        if cat_id:
            try:
                category = Category.objects.get(id=cat_id)
                ret['category_detail'] = CategorySerializer(category).data
            except Category.DoesNotExist:
                ret['category_detail'] = None
        else:
            ret['category_detail'] = None
        return ret

    def create(self, validated_data):
        brand = validated_data.pop('brand', '')
        model = validated_data.pop('model', '')
        category = validated_data.pop('category', None)
        name = validated_data.pop('name', '')
        attributes = {
            'brand': brand,
            'model': model,
            'category_id': category
        }
        product = Product.objects.create(
            name=name,
            product_type='electronic',
            attributes=attributes,
            **validated_data
        )
        return product

    def update(self, instance, validated_data):
        brand = validated_data.pop('brand', None)
        model = validated_data.pop('model', None)
        category = validated_data.pop('category', None)
        if brand is not None:
            instance.attributes['brand'] = brand
        if model is not None:
            instance.attributes['model'] = model
        if category is not None:
            instance.attributes['category_id'] = category
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.save()
        return instance
