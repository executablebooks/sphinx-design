# CSS Variables

All colors used by sphinx-design are defined as [CSS variables](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties).
Therefore they can be overriden by adding a `.css` file in a `_static` folder in your projects source folder (see [the sphinx documentation](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_css_files)):

```python
html_static_path = ['_static']
html_css_files = ['custom.css']
```

The defaults are:

```css
:root {
    --sd-color-primary: #007bff;
    --sd-color-secondary: #6c757d;
    --sd-color-success: #28a745;
    --sd-color-info: #17a2b8;
    --sd-color-warning: #f0b37e;
    --sd-color-danger: #dc3545;
    --sd-color-light: #f8f9fa;
    --sd-color-muted: #6c757d;
    --sd-color-dark: #212529;
    --sd-color-primary-highlight: #0069d9;
    --sd-color-secondary-highlight: #5c636a;
    --sd-color-success-highlight: #228e3b;
    --sd-color-info-highlight: #148a9c;
    --sd-color-warning-highlight: #cc986b;
    --sd-color-danger-highlight: #bb2d3b;
    --sd-color-light-highlight: #d3d4d5;
    --sd-color-muted-highlight: #5c636a;
    --sd-color-dark-highlight: #1c1f23;
    --sd-color-primary-text: #fff;
    --sd-color-secondary-text: #fff;
    --sd-color-success-text: #fff;
    --sd-color-info-text: #fff;
    --sd-color-warning-text: #212529;
    --sd-color-danger-text: #fff;
    --sd-color-light-text: #212529;
    --sd-color-muted-text: #fff;
    --sd-color-dark-text: #fff;
    --sd-color-shadow: rgba(0, 0, 0, 0.15);
    --sd-color-card-border: rgba(0, 0, 0, 0.125);
    --sd-color-card-border-hover: hsla(231, 99%, 66%, 1);
    --sd-color-card-background: transparent;
    --sd-color-card-text: inherit;
    --sd-color-card-header: transparent;
    --sd-color-card-footer: transparent;
    --sd-color-tabs-label-active: hsla(231, 99%, 66%, 1);
    --sd-color-tabs-label-inactive: rgba(178, 206, 245, 0.62);
    --sd-color-tabs-overline: rgb(207, 236, 238);
    --sd-color-tabs-underline: rgb(207, 236, 238);
    --sd-fontsize-tabs-label: 1rem
}
```
