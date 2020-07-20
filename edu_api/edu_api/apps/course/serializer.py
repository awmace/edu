from rest_framework.serializers import ModelSerializer

from course.models import CourseCategory, Teacher, Course, CourseChapter, CourseLesson


class CourseCategorySerializer(ModelSerializer):
    # 课程分类
    class Meta:
        model = CourseCategory
        fields = ["id", "name"]


class CourseTeacherSerializer(ModelSerializer):
    # 课程所属老师的序列化器

    class Meta:
        model = Teacher
        fields = ["id", "name", "title", "signature"]


class CourseModelSerializer(ModelSerializer):
    # 课程

    # 序列化器嵌套查询老师信息
    teacher = CourseTeacherSerializer()

    class Meta:
        model = Course
        fields = ["id", "name", "course_img", "students", "lessons", "pub_lessons", "price", "teacher", "lesson_list",
                  "discount_name", "real_price"]


class TeacherModelSerializer(ModelSerializer):
    # 课程对应的老师的信息
    class Meta:
        model = Teacher
        fields = ['id', 'name', 'role', 'signature', 'image', 'brief']


class CourseDetailModerSerializer(ModelSerializer):
    # 序列化器嵌套只能嵌套有外键关系的字段
    teacher = TeacherModelSerializer()

    # discount_name:优惠活动的名称
    class Meta:
        model = Course
        fields = ['id', 'name', 'lessons', 'students', 'pub_lessons', 'price', 'course_img', 'level_name', 'teacher',
                  'course_video', 'brief_html', 'discount_name', "real_price", "active_time"]


class CourseLessonModelSerializer(ModelSerializer):
    # 章节对应的课时
    class Meta:
        model = CourseLesson
        fields = ['id', 'name', 'free_trail']


class CourseChapterModelSerializer(ModelSerializer):
    # 章节以及章节对应的课时；序列化器嵌套
    # 一对多需要指定many
    coursesections = CourseLessonModelSerializer(many=True)

    class Meta:
        model = CourseChapter
        fields = ['id', 'chapter', 'name', 'coursesections']
