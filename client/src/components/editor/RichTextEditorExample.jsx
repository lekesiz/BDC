import React, { useState } from 'react';
import { RichTextEditor, exportContent } from './index';

const RichTextEditorExample = () => {
  const [content, setContent] = useState('');
  const [darkMode, setDarkMode] = useState(false);

  const handleImageUpload = async (file) => {
    // In a real application, you would upload the file to your server
    // and return the URL. For this example, we'll use a local URL.
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.readAsDataURL(file);
    });
  };

  const handleExport = (format, content) => {
    exportContent(format, content, 'my-document');
  };

  const sampleContent = `
    <h1>Welcome to the Rich Text Editor</h1>
    <p>This is a comprehensive rich text editor built with TipTap for the BDC client application.</p>
    
    <h2>Features</h2>
    <ul>
      <li><strong>Bold</strong>, <em>italic</em>, <u>underline</u>, and <strike>strikethrough</strike> text</li>
      <li>Multiple heading levels (H1-H6)</li>
      <li>Ordered and unordered lists</li>
      <li data-type="taskItem"><input type="checkbox" checked> Task lists with checkboxes</li>
      <li>Code blocks with syntax highlighting</li>
      <li>Mathematical formulas using LaTeX</li>
      <li>Tables and images</li>
      <li>Custom educational features</li>
    </ul>
    
    <h3>Code Example</h3>
    <pre><code class="language-javascript">function calculateSum(a, b) {
  return a + b;
}

console.log(calculateSum(5, 3)); // Output: 8</code></pre>
    
    <h3>Math Example</h3>
    <p>The quadratic formula is: <span class="math-inline" data-latex="x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"></span></p>
    
    <div class="math-block" data-latex="\\int_{a}^{b} f(x) dx = F(b) - F(a)"></div>
    
    <h3>Educational Features</h3>
    <p><span class="question-hint">This is a hint for students</span></p>
    <p><span class="correct-answer">This is the correct answer</span></p>
    
    <div class="explanation-block">
      <p>This is an explanation block that provides additional context and information about the topic.</p>
    </div>
    
    <h3>Table Example</h3>
    <table>
      <tr>
        <th>Feature</th>
        <th>Description</th>
        <th>Status</th>
      </tr>
      <tr>
        <td>Rich Text Editing</td>
        <td>Full formatting capabilities</td>
        <td>✅ Complete</td>
      </tr>
      <tr>
        <td>Math Support</td>
        <td>LaTeX formula rendering</td>
        <td>✅ Complete</td>
      </tr>
      <tr>
        <td>Mobile Support</td>
        <td>Responsive design</td>
        <td>✅ Complete</td>
      </tr>
    </table>
  `;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">Rich Text Editor Demo</h1>
        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={() => setContent(sampleContent)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Load Sample Content
          </button>
          <button
            onClick={() => setContent('')}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Clear Content
          </button>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={darkMode}
              onChange={(e) => setDarkMode(e.target.checked)}
            />
            Dark Mode
          </label>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Editor</h2>
        <RichTextEditor
          content={content}
          onChange={({ html, text, json }) => {
            setContent(html);
            console.log('Content changed:', { html, text, json });
          }}
          onImageUpload={handleImageUpload}
          placeholder="Start typing your content here..."
          darkMode={darkMode}
          showToolbar={true}
          showPreview={false}
          minHeight="300px"
          maxHeight="600px"
          onExport={handleExport}
          exportFormats={['html', 'markdown', 'json']}
        />
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Read-Only Preview</h2>
        <RichTextEditor
          content={content}
          editable={false}
          showToolbar={false}
          darkMode={darkMode}
          minHeight="200px"
          className="border-2 border-gray-300"
        />
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">HTML Output</h2>
        <pre className="bg-gray-100 p-4 rounded overflow-x-auto">
          <code>{content || '<empty>'}</code>
        </pre>
      </div>
    </div>
  );
};

export default RichTextEditorExample;