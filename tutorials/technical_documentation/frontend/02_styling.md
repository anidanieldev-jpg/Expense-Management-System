# Part 2: Styling with Utility Classes

In the web development world, "CSS vs. Utility Classes" is a hot debate. For this project, we primarily use **Tailwind CSS** (Utility Classes) because it lets us build layouts incredibly fast without leaving HTML. However, we also have a small `css/styles.css` file for things Tailwind can't easily do.

## 1. The Power of Tailwind (Utility Classes)

Open `index.html` and look at any element. You see strings like this:

```html
<div class="w-64 bg-white border-r border-gray-200 flex flex-col z-20 shadow-sm">
```

Instead of writing a CSS rule named `.sidebar` and defining 6 properties, we use pre-made classes:
- `w-64`: Width is 16rem (256px).
- `bg-white`: Background color is white.
- `border-r`: Add a border to the right side only.
- `flex flex-col`: Turn on Flexbox and arrange children in a column.
- `shadow-sm`: Add a small drop shadow.

This approach means **structure and style live together**. You don't have to hunt for a separate CSS file to see why a box is white.

## 2. When to Use Custom CSS (`css/styles.css`)

Sometimes, utility classes are too repetitive or you need a specific browser behavior. That's why we have `css/styles.css`.

### Custom Scrollbars
Browser scrollbars are ugly by default. We use custom CSS to make them sleek and grey:
```css
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
```

### Status Badges
We frequently display statuses like "Paid", "Unpaid", or "Partial". While we *could* write `<span class="bg-green-100 text-green-800 border-green-200">` every time, it's cleaner to just say `class="badge-paid"`.
```css
.badge-paid {
    background-color: #dcfce7;
    color: #166534;
    border: 1px solid #bbf7d0;
}
```
*Note: In `js/utils.js`, we have a helper function `getStatusClass()` that returns these class names based on the data.*

### Animations
To make the app feel smooth, we added a simple fade-in animation:
```css
.fade-in { animation: fadeIn 0.2s ease-in; }
```
When you open a modal or side panel, we add this class to make it appear gently rather than jarringly.

## Front-End Developer Tip 💡
Beginners often ask: *"Should I use Bootstrap or Tailwind?"*
- **Bootstrap** gives you pre-made components (like a Navbar). It's faster for prototypes but all Bootstrap sites look similar.
- **Tailwind** gives you building blocks. You build your own Navbar, but it looks exactly how you want.

In **Part 3**, we will finally touch JavaScript and see how the app starts up.
