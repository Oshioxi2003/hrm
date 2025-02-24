from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

# Create your models here.

# <-------------------------- Phòng ban -------------------------->
class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    department_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'Department'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.department_name
    

# <----------------------------- Nhân viên ------------------------->
class Employee(models.Model):
    """Model for managing employee information"""
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    # Validators
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    id_regex = RegexValidator(
        regex=r'^\d{12}$',
        message="ID must be exactly 12 digits."
    )

    # Fields
    employee_id = models.AutoField(
        primary_key=True,
        verbose_name=_('Employee ID')
    )
    
    full_name = models.CharField(
        max_length=100,
        verbose_name=_('Full Name'),
        help_text=_('Enter full name')
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date of Birth')
    )
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name=_('Gender')
    )
    
    identity_card = models.CharField(
        max_length=20,
        unique=True,
        validators=[id_regex],
        verbose_name=_('ID Card'),
        help_text=_('Enter 12-digit ID number')
    )
    
    email = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('Email')
    )
    
    phone_number = models.CharField(
        max_length=15,
        validators=[phone_regex],
        null=True,
        blank=True,
        verbose_name=_('Phone Number')
    )
    
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Address')
    )
    
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name=_('Department')
    )
    
    hire_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Hire Date')
    )

    # Meta
    class Meta:
        db_table = 'Employee'
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['-hire_date']

    def __str__(self):
        return f"{self.full_name} - {self.employee_id}"

    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        from datetime import date

        # Validate date_of_birth
        if self.date_of_birth:
            if self.date_of_birth > date.today():
                raise ValidationError({
                    'date_of_birth': _('Date of birth cannot be in the future')
                })
            
            # Check age >= 18
            age = (date.today() - self.date_of_birth).days / 365.25
            if age < 18:
                raise ValidationError({
                    'date_of_birth': _('Employee must be at least 18 years old')
                })

        # Validate hire_date
        if self.hire_date:
            if self.hire_date > date.today():
                raise ValidationError({
                    'hire_date': _('Hire date cannot be in the future')
                })

    def save(self, *args, **kwargs):
        """Override save method"""
        self.full_name = self.full_name.title()  # Capitalize name
        self.clean()  # Run validation
        super().save(*args, **kwargs)

    # Properties
    @property
    def age(self):
        """Calculate employee age"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def years_of_service(self):
        """Calculate years of service"""
        if self.hire_date:
            from datetime import date
            today = date.today()
            return today.year - self.hire_date.year - (
                (today.month, today.day) < (self.hire_date.month, self.hire_date.day)
            )
        return None
    



# <-------------------------------------- Hợp đồng lao động --------------------------------->
class LaborContract(models.Model):
    CONTRACT_TYPES = [
        ('Probation', 'Probation'),
        ('Permanent', 'Permanent'),
        ('Temporary', 'Temporary'),
    ]

    contract_id = models.AutoField(
        primary_key=True,
        verbose_name='Contract ID'
    )
    
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='labor_contracts',
        verbose_name='Employee'
    )
    
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPES,
        verbose_name='Contract Type'
    )
    
    start_date = models.DateField(
        verbose_name='Start Date'
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='End Date'
    )
    
    base_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Base Salary'
    )
    
    contract_file = models.FileField(
        upload_to='contracts/',
        null=True,
        blank=True,
        verbose_name='Attached File'
    )

    class Meta:
        db_table = 'LaborContract'
        verbose_name = 'Labor Contract'
        verbose_name_plural = 'Labor Contracts'
        ordering = ['-start_date']

    def __str__(self):
        return f"Contract-{self.contract_id} - {self.employee.full_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError('End date must be after start date')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Check if contract is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today

    @property
    def duration_months(self):
        """Calculate contract duration in months"""
        if not self.end_date:
            return None
        months = (self.end_date.year - self.start_date.year) * 12
        months += self.end_date.month - self.start_date.month
        return months