#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth.settings')
django.setup()

from django.contrib.auth.models import User
from home.models import TeacherInfo

def fix_email_case():
    print("Fixing email case mismatches...")
    
    # Find all teachers
    teachers = TeacherInfo.objects.all()
    
    for teacher in teachers:
        # Find corresponding user
        user = User.objects.filter(first_name=teacher.name).first()
        
        if user:
            print(f"Teacher: {teacher.name}")
            print(f"  User email: {user.email}")
            print(f"  Teacher email: {teacher.email}")
            
            # If emails don't match, update User email to match TeacherInfo
            if user.email.lower() != teacher.email.lower():
                print(f"  Updating User email from '{user.email}' to '{teacher.email}'")
                user.email = teacher.email
                user.save()
                print(f"  ✅ Updated!")
            else:
                print(f"  ✅ Emails already match")
        else:
            print(f"  ❌ No User found for teacher: {teacher.name}")
        
        print()

if __name__ == "__main__":
    fix_email_case()
    print("Done!") 