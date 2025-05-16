from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email

class InTimeForm(FlaskForm):
    """Form for recording vehicle in-time entry"""
    token_number = StringField('Token Number', render_kw={'readonly': True})
    vehicle_number = StringField('Vehicle Number', validators=[DataRequired(), Length(min=3, max=20)])
    driver_name = StringField('Driver Name', validators=[DataRequired(), Length(min=2, max=100)])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    item = SelectField('Item', coerce=int, validators=[DataRequired()])
    order_weight = FloatField('Order Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    tare_weight = FloatField('Tare Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Entry')

class OutTimeForm(FlaskForm):
    """Form for recording vehicle out-time entry"""
    token_number = StringField('Token Number', validators=[DataRequired()])
    loaded_weight = FloatField('Loaded Weight (kg)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Complete Entry')

class CategoryForm(FlaskForm):
    """Form for creating/editing categories"""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=50)])
    description = StringField('Description', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Save Category')

class ItemForm(FlaskForm):
    """Form for creating/editing items"""
    name = StringField('Item Name', validators=[DataRequired(), Length(min=1, max=100)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Item')

class SettingsForm(FlaskForm):
    """Form for updating system settings"""
    token_prefix = StringField('Token Prefix', validators=[DataRequired(), Length(min=2, max=2)])
    software_expiry = DateField('Software Validity', validators=[DataRequired()])
    weight_unit = SelectField('Weight Unit', choices=[('kg', 'Kilograms (kg)'), ('ton', 'Tons')], validators=[DataRequired()])
    foc_weight = FloatField('FOC Weight', validators=[DataRequired(), NumberRange(min=0)])
    foc_threshold = FloatField('FOC Threshold', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Settings')

class UserForm(FlaskForm):
    """Form for creating/editing users"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Admin User')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save User')

class ReportFilterForm(FlaskForm):
    """Form for filtering reports"""
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    submit = SubmitField('Generate Report')
