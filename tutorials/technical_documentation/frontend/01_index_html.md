# Part 1: The Blueprint - Understanding `index.html`

Welcome to this 10-part series where we deconstruct the **Expense Manager Application**. By the end, you'll understand how a modern "Single Page Application" (SPA) works without using complex frameworks like React or Vue—just pure, vanilla JavaScript.

## The Role of `index.html`

In a Single Page Application, `index.html` is the **only** HTML file the browser ever loads. It acts as a shell or skeleton. Instead of loading new HTML files when you click links, we use JavaScript to swap out the content inside this shell.

Let's break down the key parts of our blueprint.

### 1. The Head: Setting the Stage

```html
<head>
    <!-- Styling Engine -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Icon Library -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans..." rel="stylesheet">
</head>
```
- **Tailwind CSS**: We load Tailwind via CDN for quick styling. It lets us style elements using classes like `text-red-500` or `p-4` directly in HTML.
- **Lucide Icons**: A library for the beautiful icons (trash cans, pencils, wallets) you see in the app.

### 2. The Body: A Tale of Two Sections

The body is split into two main areas using Flexbox (`display: flex`):

1.  **Sidebar (`<aside>`)**: 
    - Contains the logo and navigation links.
    - Notice the IDs on links: `id="nav-expenses"`. We use these in JavaScript to know which "page" the user wants to see.
    - It stays fixed on the left while the rest of the app changes.

2.  **Main Content (`<main>`)**:
    - This is where the action happens. It takes up the remaining space (`flex-1`).
    - Inside, we have a **Viewport (`div id="viewport"`)**. This is our "stage". When you switch from Expenses to Vendors, we don't reload the page; we just rewrite the HTML inside this viewport.

### 3. Hidden Interactivity

If you scroll down, you'll see large blocks of HTML that are hidden by default:

- **Detail Panel (`id="detail-panel"`)**: A sliding drawer on the right side. It has `hidden` class initially. When you click a row, JS removes `hidden` and fills it with data.
- **Full Screen Form (`id="full-screen-form"`)**: An overlay for creating new items.
- **Modal (`id="confirm-modal"`)**: The "Are you sure?" popup.

These elements exist in the DOM from the very beginning but are invisible until JavaScript summons them.

### 4. The Brain

At the very bottom, we have the most important line:

```html
<script type="module" src="js/index.js"></script>
```

- **`type="module"`**: This tells the browser, "Hey, this isn't just a script; it's a module." This allows us to use `import` and `export` in our JavaScript files, keeping our code organized into separate files (Router, Store, Controllers) instead of one giant 5000-line spaghetti file.
- **`src="js/index.js"`**: This is the entry point. Once the HTML finishes loading, this script kicks off the entire application.

## Summary

`index.html` provides the static structure: the sidebar, the header, and the empty containers (placeholders) where our data will live. It doesn't contain any *actual* data—no expenses, no vendors. It just defines *where* that data should go.

In **Part 2**, we'll look at how we style this skeleton to make it look professional using CSS and Tailwind.
