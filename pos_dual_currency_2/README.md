# POS Dual Currency Display Module for Odoo v19

## Overview
This module adds dual currency display functionality to Odoo Point of Sale, showing real-time currency conversion on both the POS register screen and receipt printouts.

## Features

### ✅ Real-time Currency Conversion
- Displays secondary currency alongside primary currency
- Live conversion updates as items are added to cart
- Configurable exchange rates (manual or automatic)

### ✅ POS Screen Display
- Shows converted amount on Product Screen total
- Shows converted amount on Payment Screen
- Two display positions: Below or Beside the main total
- Professional styling with clear visual hierarchy

### ✅ Receipt Printing
- Dual currency amount printed on receipts
- Clear formatting with currency symbols
- Automatic decimal formatting

### ✅ Flexible Configuration
- Enable/disable per POS configuration
- Choose any currency as secondary currency
- Manual or automatic exchange rates
- Customizable display position

## Installation

1. **Copy the module** to your Odoo addons directory:
   ```bash
   cp -r pos_dual_currency /path/to/odoo/addons/
   ```

2. **Update the apps list**:
   - Go to Apps menu
   - Click "Update Apps List"
   - Remove the "Apps" filter
   - Search for "POS Dual Currency Display"

3. **Install the module**:
   - Click Install button

## Configuration

1. **Navigate to POS Configuration**:
   ```
   Point of Sale → Configuration → Point of Sale
   ```

2. **Select your POS** and go to the **"Dual Currency"** tab

3. **Configure Settings**:
   - ✅ **Enable Dual Currency Display**: Check this box
   - **Secondary Currency**: Select the currency to display (e.g., AED, EUR, GBP)
   - **Rate Type**: 
     - *Manual Rate*: Enter custom exchange rate
     - *Automatic Rate*: Use system currency rates
   - **Exchange Rate**: Set the conversion rate (e.g., 3.75 for USD to AED)
   - **Display Position**:
     - *Below Total*: Shows secondary currency under main total
     - *Beside Total*: Shows secondary currency next to main total

4. **Save** the configuration

## Usage

### In POS Session

1. **Open POS**:
   - Start a new POS session
   - The dual currency feature will be active automatically

2. **Product Screen**:
   - Add items to cart
   - Main total displays in primary currency
   - Secondary currency shows in real-time with "≈" symbol
   
3. **Payment Screen**:
   - Both currencies show the amount due
   - Updates as payments are added

4. **Receipt**:
   - After payment, receipt shows both currencies
   - Dual currency appears below the total with "≈" symbol

### Example Display

**Below Position:**
```
Total: $100.00
≈ AED 367.50
```

**Beside Position:**
```
Total: $100.00 / AED 367.50
```

## Exchange Rate Examples

| From → To | Example Rate | $100.00 converts to |
|-----------|--------------|---------------------|
| USD → AED | 3.675        | AED 367.50         |
| USD → EUR | 0.85         | EUR 85.00          |
| EUR → USD | 1.18         | USD 118.00         |
| GBP → USD | 1.25         | USD 125.00         |

## Technical Details

### Module Structure
```
pos_dual_currency/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── pos_config.py
│   └── pos_order.py
├── views/
│   ├── pos_config_views.xml
│   └── pos_dual_currency_templates.xml
├── static/
│   └── src/
│       ├── app/
│       │   ├── models/
│       │   │   └── pos_store.js
│       │   └── screens/
│       │       ├── product_screen/
│       │       │   ├── product_screen.js
│       │       │   └── product_screen.xml
│       │       └── payment_screen/
│       │           ├── payment_screen.js
│       │           └── payment_screen.xml
│       └── css/
│           └── pos_dual_currency.css
└── security/
    └── ir.model.access.csv
```

### Dependencies
- `point_of_sale`
- `base`

### Compatibility
- Odoo Version: 19.0
- License: LGPL-3

## Customization

### Change Colors
Edit `static/src/css/pos_dual_currency.css`:
```css
.dual-currency-total.below {
    color: #7c7bad; /* Change this color */
}
```

### Adjust Font Size
```css
.dual-currency-total.below {
    font-size: 24px; /* Change size */
}
```

### Modify Decimal Places
Edit `models/pos_config.py` in the `get_dual_currency_config` method to change decimal places.

## Troubleshooting

### Dual Currency Not Showing
1. ✅ Check if module is installed
2. ✅ Verify "Enable Dual Currency Display" is checked
3. ✅ Ensure a secondary currency is selected
4. ✅ Restart POS session after configuration changes
5. ✅ Clear browser cache

### Incorrect Exchange Rate
1. If using **Automatic Rate**: Check system currency rates under Accounting → Configuration → Currencies
2. If using **Manual Rate**: Verify the rate entered in POS configuration
3. Exchange rate should convert FROM primary TO secondary (multiply, not divide)

### Receipt Not Showing Dual Currency
1. Ensure configuration is saved
2. Close and reopen POS session
3. Check that order is created after module installation

## Support

For issues or feature requests:
1. Check Odoo logs for error messages
2. Verify all dependencies are installed
3. Ensure Odoo assets are rebuilt after installation

## Credits

**Author**: Your Company  
**Version**: 19.0.1.0.0  
**License**: LGPL-3

---

### Example Configuration Screenshots

**Configuration Page** (Dual Currency Tab):
- Enable checkbox
- Currency selector
- Rate type radio buttons
- Exchange rate field
- Display position options

**POS Screen** (Product View):
- Main total in USD
- "≈ AED 367.50" below or beside

**Receipt Print**:
- Order details
- Total: $100.00
- ≈ AED 367.50 (in italics)

## Version History

### 19.0.1.0.0 (2026-01-22)
- Initial release
- Real-time dual currency display
- Receipt integration
- Configurable exchange rates
- Two display positions (below/beside)
