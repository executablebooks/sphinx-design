(special)=

# Additional

These are additional components that are not part of the standard Materials Design or Bootstrap systems.

## `article-info`

This directive is used to display a block of information about an article,
normally positioned just below the title of the article (shown below with non-standard outline).

```{article-info}
:avatar: images/ebp-logo.png
:avatar-link: https://executablebooks.org/
:avatar-outline: muted
:author: Executable Books
:date: "Jul 24, 2021"
:read-time: "5 min read"
:class-container: sd-p-2 sd-outline-muted sd-rounded-1
```

`````{dropdown} Syntax
:icon: code
:color: primary

````{tab-set-code}
```{literalinclude} ./snippets/myst/article-info.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/article-info.txt
:language: rst
```
````
`````

The `author`, `date`, and `read-time` options are parsed as syntax,
so you can use substitutions like:

- `date`
  - MyST: `` :date: "{sub-ref}`today`" ``
  - RST: `:data: |today|`
- `read-time`
  - MyST: `` :read-time: "{sub-ref}`wordcount-minutes` min read" ``

### options

avatar
: A URI (relative file path or URL) to an image for use as the avatar (a user portrait, logo or branded graphic).

avatar-alt
: Alternative text for the avatar.

avatar-link
: A URL to link to if the avatar icon is clicked.

avatar-outline
: A semantic color to use for the outline of the avatar.

author
: Text to display in the author of of the article.

date
: Text to display in the date of the article.

read-time
: Text to indicate the time to read the article.

class-container
: Additional CSS classes for the container element.

class-avatar
: Additional CSS classes for the avatar element.
