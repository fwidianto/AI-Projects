# Inventory Tracker - Specification

## Concept & Vision

A sleek, minimalist inventory tracker with a warm, approachable aesthetic. The interface feels like a well-organized physical ledger — clean, functional, but with subtle personality. It prioritizes clarity and speed: add items in seconds, search instantly, and get visual feedback that makes inventory management feel satisfying rather than tedious.

## Design Language

### Aesthetic Direction
Industrial-minimal with warm accents — inspired by Scandinavian design meets warehouse efficiency. Muted backgrounds with crisp white cards, accented by a warm amber/orange for interactive elements.

### Color Palette
- **Primary Background**: `#f8f7f4` — warm off-white
- **Card Background**: `#ffffff` — pure white
- **Primary Text**: `#2d2a26` — warm charcoal
- **Secondary Text**: `#6b6560` — muted brown-gray
- **Accent**: `#e07a3d` — warm amber-orange
- **Accent Hover**: `#c96a32` — deeper amber
- **Success**: `#4a9f6e` — muted green
- **Danger**: `#d64545` — soft red
- **Border**: `#e8e6e1` — subtle warm gray
- **Shadow**: `rgba(45, 42, 38, 0.08)` — warm shadow

### Typography
- **Headings**: `DM Sans` (Google Font) — geometric, friendly, modern
- **Body/Data**: `IBM Plex Mono` (Google Font) — monospace for that ledger feel, excellent for numbers

### Spatial System
- Base unit: 8px
- Card padding: 24px
- Section gaps: 32px
- Border radius: 12px (cards), 8px (inputs/buttons)

### Motion Philosophy
- Subtle, purposeful animations that confirm actions
- Cards fade in with slight upward motion (200ms ease-out)
- Button hover: scale 1.02 with shadow lift
- Delete: fade out + slide left (150ms)
- Low stock items: gentle pulse animation on the quantity badge

### Visual Assets
- Lucide icons via CDN (consistent stroke weight, friendly style)
- No images — pure CSS/SVG decorative elements
- Decorative grid pattern in header area (subtle, 5% opacity)

## Layout & Structure

### Page Structure
1. **Header** — App title with decorative grid pattern background, subtle and sophisticated
2. **Add Item Form** — Horizontal card with inputs for name, quantity, category, min stock threshold
3. **Inventory Stats** — Quick glance cards showing total items, low stock alerts, categories count
4. **Search & Filter Bar** — Sticky search with category filter dropdown
5. **Inventory Table** — Main content: sortable columns, inline editing, action buttons
6. **Empty State** — Friendly illustration/message when no items exist

### Responsive Strategy
- Desktop: Full table view with all columns
- Tablet (< 900px): Condensed columns, hide category
- Mobile (< 600px): Card-based list instead of table

## Features & Interactions

### Core Features
1. **Add Item**
   - Name (required): Text input, auto-uppercase first letter
   - Quantity: Number input with increment/decrement buttons
   - Category: Dropdown (Electronics, Clothing, Food, Tools, Office, Other)
   - Min Stock: Number input for low-stock threshold
   - Submit: Adds to localStorage, clears form, shows success feedback

2. **View Inventory**
   - Table displays: Name, Quantity (with status indicator), Category, Min Stock, Actions
   - Quantity badges: Green (> min), Yellow (at min), Red (< min)
   - Sortable by clicking column headers

3. **Edit Item**
   - Click edit icon → row becomes editable inline
   - Save/Cancel buttons appear
   - Escape key cancels, Enter key saves

4. **Delete Item**
   - Click trash icon → confirmation tooltip
   - Confirm deletes with fade animation
   - Undo option appears for 5 seconds (toast notification)

5. **Search & Filter**
   - Real-time search by name
   - Category filter dropdown
   - Combined filtering (search + category)

6. **Low Stock Alerts**
   - Stats card shows count of low-stock items
   - Items below threshold have visual indicator
   - Pulse animation on critical items

### Edge Cases
- Empty inventory: Friendly empty state with call-to-action
- Duplicate names: Allowed (different SKUs implied)
- Invalid quantity: Minimum 0, must be integer
- Very long names: Truncate with ellipsis, full name on hover

## Component Inventory

### Header
- Background: Primary with grid pattern overlay
- Title: Large, bold, accent color on first letter
- States: Static (no interaction)

### Add Item Form Card
- White card with shadow
- Inputs with labels above
- Add button: Full accent color, white text
- States: Default, submitting (brief loading), success (brief green flash)

### Stat Cards (3 across)
- Small white cards
- Icon + number + label
- Total items, Low stock count (red if > 0), Categories
- States: Default, hover (slight lift)

### Search Bar
- Sticky on scroll
- Left search icon, right clear button (when has value)
- Category dropdown beside it
- States: Empty, has value, focused

### Inventory Table
- Header row: Bold, sortable columns with sort indicators
- Data rows: Alternating subtle backgrounds
- Quantity badge: Colored based on stock level
- Actions: Icon buttons (edit, delete)
- States: Empty, populated, loading, row hover, row editing

### Item Row (Editing)
- Inputs replace text
- Save (green) and Cancel (gray) buttons
- States: Viewing, editing

### Empty State
- Centered content
- Decorative icon (box or clipboard)
- Friendly message + CTA button
- States: Static

### Toast Notification
- Fixed bottom-right
- Auto-dismiss after 5 seconds
- Undo action link
- States: Success (green), Info (blue), Error (red)

## Technical Approach

### Stack
- Single HTML file with embedded CSS and JavaScript
- No build tools, frameworks, or external JS
- Google Fonts via CDN
- Lucide icons via CDN
- localStorage for persistence

### Data Model
```javascript
Item {
  id: string (UUID),
  name: string,
  quantity: number,
  category: string,
  minStock: number,
  createdAt: timestamp,
  updatedAt: timestamp
}
```

### State Management
- Single source of truth: items array in memory
- Sync with localStorage on every mutation
- Render function re-renders table on state change

### Key Functions
- `loadItems()`: Load from localStorage
- `saveItems()`: Persist to localStorage
- `addItem(data)`: Validate and add
- `updateItem(id, data)`: Update existing
- `deleteItem(id)`: Remove with undo support
- `renderTable()`: Re-render inventory list
- `filterItems(query, category)`: Filter logic
- `sortItems(column, direction)`: Sort logic