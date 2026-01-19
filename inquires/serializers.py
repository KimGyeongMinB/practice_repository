from rest_framework import serializers
from .models import Inquiry, InquiryImage

# 이미지
class InquiryImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InquiryImage
        fields = ("image", )

# 문의사항 시리얼라이저
class InquirySerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.nickname")
    image = serializers.SerializerMethodField()

    class Meta:
        model = Inquiry
        fields = "__all__"

    # 이미지 가져오기
    def get_image(self, obj):
        image = obj.image.all()
        return InquiryImageSerializer(image, many=True).data
    
    def create(self, validated_data):
        instance = Inquiry.objects.create(**validated_data)
        image_set = getattr(self.context.get("request"), "FILES", None)
        for image_data in image_set.getlist("image"):
            InquiryImage.objects.create(inquiry=instance, image=image_data)
        return instance

class InquiryRestoreSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.nickname")

    class Meta:
        model = Inquiry
        fields = "__all__"

# 마이페이지 역참조용 시리얼라이저
class InquirySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["id", "title", "created_at", "deleted_at", "hard_deleted_at"]