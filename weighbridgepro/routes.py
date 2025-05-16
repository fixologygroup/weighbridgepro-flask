from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import csv
import io
from models import WeighbridgeEntry, Category, Item, Setting, User
from forms import InTimeForm, OutTimeForm, CategoryForm, ItemForm, SettingsForm, UserForm, ReportFilterForm
from utils import generate_token_number, calculate_foc, calculate_differences, is_software_valid, simulate_weight_reading
from app import db

def register_routes(app):
    
    @app.before_request
    def check_software_validity():
        """Check software validity before processing any request"""
        # Skip checking for static files
        if request.path.startswith('/static'):
            return
            
        if not is_software_valid():
            # If software is expired, only allow access to renewal page
            if request.path != '/admin/renew':
                flash('Software license has expired. Please contact administrator.', 'danger')
                return redirect(url_for('admin_renew'))
    
    @app.route('/')
    def dashboard():
        """Main dashboard/landing page"""
        # Get latest entries for display
        recent_entries = WeighbridgeEntry.query.order_by(WeighbridgeEntry.id.desc()).limit(5).all()
        
        # Get metrics for dashboard
        total_entries = WeighbridgeEntry.query.count()
        pending_entries = WeighbridgeEntry.query.filter_by(is_completed=False).count()
        completed_entries = WeighbridgeEntry.query.filter_by(is_completed=True).count()
        
        # Calculate today's entries
        today = datetime.now().date()
        today_entries = WeighbridgeEntry.query.filter(
            db.func.date(WeighbridgeEntry.in_time) == today
        ).count()
        
        return render_template(
            'dashboard.html', 
            recent_entries=recent_entries,
            total_entries=total_entries,
            pending_entries=pending_entries,
            completed_entries=completed_entries,
            today_entries=today_entries
        )
    
    @app.route('/in-time', methods=['GET', 'POST'])
    def in_time():
        """Handle In-Time Token form"""
        form = InTimeForm()
        
        # Populate the category dropdown
        form.category.choices = [(c.id, c.name) for c in Category.query.all()]
        
        # Default item choices (will be updated via AJAX)
        if form.category.data:
            form.item.choices = [(i.id, i.name) for i in Item.query.filter_by(category_id=form.category.data).all()]
        else:
            form.item.choices = [(i.id, i.name) for i in Item.query.all()]
        
        # Generate a new token number
        token_number = generate_token_number()
        form.token_number.data = token_number
        
        if form.validate_on_submit():
            # Create a new entry
            entry = WeighbridgeEntry(
                token_number=form.token_number.data,
                vehicle_number=form.vehicle_number.data,
                driver_name=form.driver_name.data,
                mobile_number=form.mobile_number.data,
                category_id=form.category.data,
                item_id=form.item.data,
                order_weight=form.order_weight.data,
                tare_weight=form.tare_weight.data,
                in_time=datetime.now(),
                is_completed=False
            )
            
            db.session.add(entry)
            db.session.commit()
            
            flash(f'In-Time entry created successfully. Token: {entry.token_number}', 'success')
            return redirect(url_for('in_time'))
        
        return render_template('in_time.html', form=form)
    
    @app.route('/get-items/<int:category_id>')
    def get_items(category_id):
        """AJAX endpoint to get items for a specific category"""
        items = Item.query.filter_by(category_id=category_id).all()
        return jsonify({
            'items': [{'id': item.id, 'name': item.name} for item in items]
        })
    
    @app.route('/simulate-weight')
    def simulate_weight():
        """AJAX endpoint to simulate a weight reading"""
        weight = simulate_weight_reading()
        return jsonify({'weight': weight})
    
    @app.route('/out-time', methods=['GET', 'POST'])
    def out_time():
        """Handle Out-Time Token form"""
        form = OutTimeForm()
        entry = None
        calculations = None
        
        # If token number provided via GET or POST
        token_number = request.args.get('token_number') or form.token_number.data
        
        if token_number:
            # Find the entry
            entry = WeighbridgeEntry.query.filter_by(token_number=token_number).first()
            
            if not entry:
                flash('Entry not found. Please check the token number.', 'danger')
            elif entry.is_completed:
                flash('This entry has already been completed.', 'warning')
        
        if form.validate_on_submit() and entry and not entry.is_completed:
            # Calculate values
            loaded_weight = form.loaded_weight.data
            calculated_values = calculate_differences(entry, loaded_weight)
            
            # Update the entry
            entry.loaded_weight = calculated_values['loaded_weight']
            entry.net_weight = calculated_values['net_weight']
            entry.foc_weight = calculated_values['foc_weight']
            entry.difference_weight = calculated_values['difference_weight']
            entry.out_time = datetime.now()
            entry.is_completed = True
            
            db.session.commit()
            
            flash('Out-Time entry completed successfully.', 'success')
            return redirect(url_for('out_time'))
        
        # If entry found but not submitted, show calculated fields for preview
        if entry and not entry.is_completed and request.method == 'GET':
            # Default loaded weight for preview
            dummy_loaded = entry.tare_weight + entry.order_weight
            calculations = calculate_differences(entry, dummy_loaded)
        
        return render_template('out_time.html', form=form, entry=entry, calculations=calculations)
    
    @app.route('/preview-calculations')
    def preview_calculations():
        """AJAX endpoint to preview calculations based on loaded weight"""
        token_number = request.args.get('token_number')
        loaded_weight = float(request.args.get('loaded_weight', 0))
        
        entry = WeighbridgeEntry.query.filter_by(token_number=token_number).first()
        
        if not entry:
            return jsonify({'error': 'Entry not found'})
        
        calculations = calculate_differences(entry, loaded_weight)
        return jsonify(calculations)
    
    @app.route('/admin')
    def admin():
        """Admin panel landing page"""
        # Count statistics for admin dashboard
        categories_count = Category.query.count()
        items_count = Item.query.count()
        users_count = User.query.count()
        
        # Get settings for display
        settings = {s.key: s.value for s in Setting.query.all()}
        
        return render_template(
            'admin.html',
            categories_count=categories_count,
            items_count=items_count,
            users_count=users_count,
            settings=settings
        )
    
    @app.route('/admin/categories', methods=['GET', 'POST'])
    def admin_categories():
        """Manage categories"""
        form = CategoryForm()
        
        # Handle form submission for new category
        if form.validate_on_submit():
            category = Category(name=form.name.data, description=form.description.data)
            db.session.add(category)
            db.session.commit()
            
            flash('Category added successfully.', 'success')
            return redirect(url_for('admin_categories'))
        
        # Get all categories for display
        categories = Category.query.all()
        
        return render_template('admin_categories.html', form=form, categories=categories)
    
    @app.route('/admin/categories/edit/<int:id>', methods=['GET', 'POST'])
    def admin_edit_category(id):
        """Edit a category"""
        category = Category.query.get_or_404(id)
        form = CategoryForm(obj=category)
        
        if form.validate_on_submit():
            category.name = form.name.data
            category.description = form.description.data
            db.session.commit()
            
            flash('Category updated successfully.', 'success')
            return redirect(url_for('admin_categories'))
        
        return render_template('admin_edit_category.html', form=form, category=category)
    
    @app.route('/admin/categories/delete/<int:id>', methods=['POST'])
    def admin_delete_category(id):
        """Delete a category"""
        category = Category.query.get_or_404(id)
        
        # Check if category has items
        if category.items:
            flash('Cannot delete category with associated items.', 'danger')
            return redirect(url_for('admin_categories'))
        
        # Check if category has entries
        if category.entries:
            flash('Cannot delete category with associated entries.', 'danger')
            return redirect(url_for('admin_categories'))
        
        db.session.delete(category)
        db.session.commit()
        
        flash('Category deleted successfully.', 'success')
        return redirect(url_for('admin_categories'))
    
    @app.route('/admin/items', methods=['GET', 'POST'])
    def admin_items():
        """Manage items"""
        form = ItemForm()
        
        # Populate category dropdown
        form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
        
        # Handle form submission for new item
        if form.validate_on_submit():
            item = Item(name=form.name.data, category_id=form.category_id.data)
            db.session.add(item)
            db.session.commit()
            
            flash('Item added successfully.', 'success')
            return redirect(url_for('admin_items'))
        
        # Get all items with categories for display
        items = Item.query.join(Category).all()
        
        return render_template('admin_items.html', form=form, items=items)
    
    @app.route('/admin/items/edit/<int:id>', methods=['GET', 'POST'])
    def admin_edit_item(id):
        """Edit an item"""
        item = Item.query.get_or_404(id)
        form = ItemForm(obj=item)
        
        # Populate category dropdown
        form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
        
        if form.validate_on_submit():
            item.name = form.name.data
            item.category_id = form.category_id.data
            db.session.commit()
            
            flash('Item updated successfully.', 'success')
            return redirect(url_for('admin_items'))
        
        return render_template('admin_edit_item.html', form=form, item=item)
    
    @app.route('/admin/items/delete/<int:id>', methods=['POST'])
    def admin_delete_item(id):
        """Delete an item"""
        item = Item.query.get_or_404(id)
        
        # Check if item has entries
        if item.entries:
            flash('Cannot delete item with associated entries.', 'danger')
            return redirect(url_for('admin_items'))
        
        db.session.delete(item)
        db.session.commit()
        
        flash('Item deleted successfully.', 'success')
        return redirect(url_for('admin_items'))
    
    @app.route('/admin/settings', methods=['GET', 'POST'])
    def admin_settings():
        """Manage system settings"""
        # Get current settings
        settings = {s.key: s.value for s in Setting.query.all()}
        
        # Create form and populate with current values
        form = SettingsForm()
        
        if request.method == 'GET':
            # Populate form with current settings
            form.token_prefix.data = settings.get('token_prefix', 'AB')
            
            # Handle date format for software_expiry
            try:
                form.software_expiry.data = datetime.strptime(
                    settings.get('software_expiry', datetime.now().date().isoformat()),
                    '%Y-%m-%d'
                ).date()
            except ValueError:
                form.software_expiry.data = datetime.now().date()
            
            # Set weight unit dropdown
            form.weight_unit.data = settings.get('weight_unit', 'kg')
                
            form.foc_weight.data = float(settings.get('foc_weight', 500))
            form.foc_threshold.data = float(settings.get('foc_threshold', 10000))
        
        if form.validate_on_submit():
            # Update settings
            for key, value in {
                'token_prefix': form.token_prefix.data,
                'software_expiry': form.software_expiry.data.isoformat(),
                'weight_unit': form.weight_unit.data, 
                'foc_weight': str(form.foc_weight.data),
                'foc_threshold': str(form.foc_threshold.data)
            }.items():
                setting = Setting.query.filter_by(key=key).first()
                if setting:
                    setting.value = value
                else:
                    setting = Setting(key=key, value=value)
                    db.session.add(setting)
            
            db.session.commit()
            flash('Settings updated successfully.', 'success')
            return redirect(url_for('admin_settings'))
        
        return render_template('admin_settings.html', form=form, settings=settings)
    
    @app.route('/admin/renew')
    def admin_renew():
        """Software renewal page"""
        # Get current expiry date
        expiry_setting = Setting.query.filter_by(key="software_expiry").first()
        expiry_date = datetime.now().date()
        
        if expiry_setting:
            try:
                expiry_date = datetime.strptime(expiry_setting.value, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Calculate days until expiry or days since expiry
        today = datetime.now().date()
        days_diff = (expiry_date - today).days
        
        return render_template('admin_renew.html', expiry_date=expiry_date, days_diff=days_diff)
    
    @app.route('/reports', methods=['GET', 'POST'])
    def reports():
        """Reports page with filtering options"""
        form = ReportFilterForm()
        
        # Set default date range to current month
        if request.method == 'GET':
            today = datetime.now().date()
            form.start_date.data = today.replace(day=1)  # First day of current month
            form.end_date.data = today
        
        # Populate category filter dropdown
        categories = Category.query.all()
        form.category.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in categories]
        
        # Initialize entries as None (no search performed yet)
        entries = None
        
        if form.validate_on_submit():
            # Build the query with filters
            query = WeighbridgeEntry.query.filter(
                db.func.date(WeighbridgeEntry.in_time) >= form.start_date.data,
                db.func.date(WeighbridgeEntry.in_time) <= form.end_date.data
            )
            
            # Apply category filter if specified
            if form.category.data != 0:  # 0 means "All Categories"
                query = query.filter(WeighbridgeEntry.category_id == form.category.data)
            
            # Execute query and get results
            entries = query.order_by(WeighbridgeEntry.in_time.desc()).all()
        
        return render_template('reports.html', form=form, entries=entries)
    
    @app.route('/reports/export', methods=['POST'])
    def export_report():
        """Export report data to CSV"""
        # Get filter parameters from form
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        category_id = int(request.form.get('category', 0))
        
        # Build the query with filters
        query = WeighbridgeEntry.query.filter(
            db.func.date(WeighbridgeEntry.in_time) >= start_date,
            db.func.date(WeighbridgeEntry.in_time) <= end_date
        )
        
        # Apply category filter if specified
        if category_id != 0:  # 0 means "All Categories"
            query = query.filter(WeighbridgeEntry.category_id == category_id)
        
        # Execute query and get results
        entries = query.order_by(WeighbridgeEntry.in_time.desc()).all()
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header row
        writer.writerow([
            'Token No', 'Vehicle', 'Driver', 'Category', 'Item', 
            'Tare Weight', 'Loaded Weight', 'Net Weight', 'FOC Weight',
            'In-Time', 'Out-Time'
        ])
        
        # Write data rows
        for entry in entries:
            writer.writerow([
                entry.token_number,
                entry.vehicle_number,
                entry.driver_name,
                entry.category.name,
                entry.item.name,
                entry.tare_weight,
                entry.loaded_weight or '',
                entry.net_weight or '',
                entry.foc_weight or '',
                entry.in_time.strftime('%Y-%m-%d %H:%M'),
                entry.out_time.strftime('%Y-%m-%d %H:%M') if entry.out_time else ''
            ])
        
        # Prepare the response
        from flask import Response
        output.seek(0)
        
        filename = f"weighbridge_report_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"
        
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
