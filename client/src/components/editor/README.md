# Rich Text Editor Component

A comprehensive rich text editor built with TipTap for the BDC client application, specifically designed for educational content creation.

## Features

### Basic Formatting
- **Bold** (Ctrl+B)
- *Italic* (Ctrl+I)
- <u>Underline</u> (Ctrl+U)
- ~~Strikethrough~~
- Highlight text with colors

### Structure
- Headers (H1-H6)
- Bullet lists
- Numbered lists
- Task lists with checkboxes
- Tables with headers

### Code Support
- Inline code snippets
- Code blocks with syntax highlighting
- Support for multiple languages (JavaScript, Python, Java, C++, CSS, HTML, SQL, Bash)

### Mathematical Formulas
- LaTeX support for mathematical expressions
- Inline formulas (e.g., $x^2 + y^2 = z^2$)
- Block formulas for complex equations
- Visual formula editor with live preview

### Media
- Image upload and embedding
- Drag & drop image support
- Paste images from clipboard
- Base64 and URL image support

### Educational Features
- **Question Hints**: Highlight helpful hints for students
- **Correct Answer Highlighting**: Mark the correct answers distinctly
- **Explanation Blocks**: Add detailed explanations with special formatting

### Additional Features
- Text alignment (left, center, right, justify)
- Links with target="_blank"
- Undo/Redo with history (Ctrl+Z/Ctrl+Y)
- Preview mode
- Export to HTML, Markdown, and JSON
- Dark mode support
- Mobile-friendly responsive design

## Usage

### Basic Implementation

```jsx
import { RichTextEditor } from '@/components/editor';

function MyComponent() {
  const [content, setContent] = useState('');

  const handleChange = ({ html, text, json }) => {
    setContent(html);
    // You can also access plain text and JSON representations
  };

  return (
    <RichTextEditor
      content={content}
      onChange={handleChange}
      placeholder="Start typing..."
    />
  );
}
```

### With Image Upload

```jsx
const handleImageUpload = async (file) => {
  // Upload file to your server
  const formData = new FormData();
  formData.append('image', file);
  
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });
  
  const { url } = await response.json();
  return url;
};

<RichTextEditor
  content={content}
  onChange={handleChange}
  onImageUpload={handleImageUpload}
/>
```

### Export Functionality

```jsx
const handleExport = (format, content) => {
  // The component provides the content in the requested format
  console.log(`Exporting as ${format}:`, content);
  
  // You can also use the built-in export function
  exportContent(format, content, 'my-document');
};

<RichTextEditor
  content={content}
  onChange={handleChange}
  onExport={handleExport}
  exportFormats={['html', 'markdown', 'json']}
/>
```

### Read-Only Mode

```jsx
<RichTextEditor
  content={content}
  editable={false}
  showToolbar={false}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| content | string | '' | HTML content to display in the editor |
| onChange | function | - | Callback when content changes. Receives `{ html, text, json }` |
| onImageUpload | function | - | Async function to handle image uploads. Should return image URL |
| placeholder | string | 'Start typing...' | Placeholder text when editor is empty |
| editable | boolean | true | Whether the editor is editable |
| showToolbar | boolean | true | Show/hide the toolbar |
| showPreview | boolean | false | Start in preview mode |
| className | string | '' | Additional CSS classes |
| height | string | 'auto' | Editor height |
| minHeight | string | '200px' | Minimum editor height |
| maxHeight | string | '600px' | Maximum editor height |
| darkMode | boolean | false | Enable dark mode |
| onExport | function | - | Callback for export functionality |
| exportFormats | array | ['html', 'markdown'] | Available export formats |

## Keyboard Shortcuts

- **Bold**: Ctrl/Cmd + B
- **Italic**: Ctrl/Cmd + I
- **Underline**: Ctrl/Cmd + U
- **Undo**: Ctrl/Cmd + Z
- **Redo**: Ctrl/Cmd + Y
- **Question Hint**: Ctrl/Cmd + Shift + H
- **Correct Answer**: Ctrl/Cmd + Shift + C
- **Explanation Block**: Ctrl/Cmd + Shift + E
- **Math Formula**: Ctrl/Cmd + Shift + M

## Custom Extensions

### Question Hint
Wrap text in a hint block for students:
```jsx
editor.chain().focus().toggleQuestionHint().run()
```

### Correct Answer
Highlight the correct answer:
```jsx
editor.chain().focus().toggleCorrectAnswer().run()
```

### Explanation Block
Add an explanation section:
```jsx
editor.chain().focus().toggleExplanationBlock().run()
```

### Mathematics
Insert a math formula:
```jsx
editor.chain().focus().insertMath({ latex: 'x^2', display: false }).run()
```

## Styling

The component uses Tailwind CSS classes and includes a comprehensive stylesheet. You can customize the appearance by:

1. Overriding CSS variables
2. Adding custom classes via the `className` prop
3. Modifying the `RichTextEditor.css` file

### Dark Mode
The component supports dark mode through the `darkMode` prop, which applies appropriate styles to all elements.

## Integration with QuestionEditor

The RichTextEditor is integrated into the QuestionEditor component for rich question text editing:

```jsx
<RichTextEditor
  content={questionContent}
  onChange={({ html }) => {
    setValue(`questions.${index}.question_text`, html);
  }}
  placeholder="Enter your question here..."
  minHeight="120px"
/>
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Android)

## Dependencies

- @tiptap/react
- @tiptap/starter-kit
- Various @tiptap extensions
- katex (for math rendering)
- lowlight (for syntax highlighting)
- lucide-react (for icons)