#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth.settings')
django.setup()

from django.contrib.auth.models import User
from home.models import TeacherInfo

def check_professor_account(email):
    print(f"Checking for professor with email: {email}")
    print("=" * 50)
    
    # Check User model
    users = User.objects.filter(email__iexact=email)
    print(f"Users found with this email: {users.count()}")
    for user in users:
        print(f"  - Username: {user.username}")
        print(f"  - Full name: {user.get_full_name()}")
        print(f"  - Email: {user.email}")
        print(f"  - Is active: {user.is_active}")
    
    # Check TeacherInfo model
    teachers = TeacherInfo.objects.filter(email__iexact=email)
    print(f"\nTeacherInfo found with this email: {teachers.count()}")
    for teacher in teachers:
        print(f"  - Name: {teacher.name}")
        print(f"  - Email: {teacher.email}")
        print(f"  - Unique ID: {teacher.unique_id}")
        print(f"  - Department: {teacher.department}")
    
    # Check for case variations
    print(f"\nChecking for case variations...")
    all_users = User.objects.all()
    matching_users = [u for u in all_users if u.email.lower() == email.lower()]
    print(f"Users with case-insensitive match: {len(matching_users)}")
    
    all_teachers = TeacherInfo.objects.all()
    matching_teachers = [t for t in all_teachers if t.email.lower() == email.lower()]
    print(f"Teachers with case-insensitive match: {len(matching_teachers)}")
    
    return len(users) > 0 or len(teachers) > 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_professor.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    exists = check_professor_account(email)
    
    if exists:
        print(f"\n✅ Account found! The issue might be with password or case sensitivity.")
    else:
        print(f"\n❌ No account found with email: {email}")
        print("You may need to register again or check if you used a different email.") 