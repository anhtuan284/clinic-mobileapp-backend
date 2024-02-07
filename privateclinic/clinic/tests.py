from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import Group, User, Permission

# Tạo nhóm
nurse_group = Group.objects.create(name='Nurse')
doctor_group = Group.objects.create(name='Doctor')
patient_group = Group.objects.create(name='Patient')

# Gán người dùng vào nhóm tương ứng
# user1 = User.objects.get(username='nurse1')
# user2 = User.objects.get(username='doctor1')
# user3 = User.objects.get(username='patient1')

# nurse_group.user_set.add(user1)
# doctor_group.user_set.add(user2)
# patient_group.user_set.add(user3)

# Tạo quyền truy cập
can_view_patient_info = Permission.objects.create(codename='view_patient_info', name='Can view patient information')
can_create_appointment = Permission.objects.create(codename='create_appointment', name='Can create appointment')
can_update_prescription = Permission.objects.create(codename='update_prescription', name='Can update prescription')

