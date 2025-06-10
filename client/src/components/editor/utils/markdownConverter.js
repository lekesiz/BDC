// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Basic markdown converter for TipTap
export const htmlToMarkdown = (html) => {
  // Create a temporary div to parse HTML
  const div = document.createElement('div');
  div.innerHTML = html;
  let markdown = '';
  const convertNode = (node, level = 0) => {
    if (node.nodeType === Node.TEXT_NODE) {
      return node.textContent;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) {
      return '';
    }
    const tagName = node.tagName.toLowerCase();
    const children = Array.from(node.childNodes).
    map((child) => convertNode(child, level)).
    join('');
    switch (tagName) {
      case 'h1':
        return `# ${children}\n\n`;
      case 'h2':
        return `## ${children}\n\n`;
      case 'h3':
        return `### ${children}\n\n`;
      case 'h4':
        return `#### ${children}\n\n`;
      case 'h5':
        return `##### ${children}\n\n`;
      case 'h6':
        return `###### ${children}\n\n`;
      case 'p':
        return `${children}\n\n`;
      case 'strong':
      case 'b':
        return `**${children}**`;
      case 'em':
      case 'i':
        return `*${children}*`;
      case 'u':
        return `<u>${children}</u>`;
      case 'strike':
      case 's':
      case 'del':
        return `~~${children}~~`;
      case 'code':
        if (node.parentNode.tagName === 'PRE') {
          return children;
        }
        return `\`${children}\``;
      case 'pre':
        const lang = node.querySelector('code')?.className?.match(/language-(\w+)/)?.[1] || '';
        return `\`\`\`${lang}\n${children}\n\`\`\`\n\n`;
      case 'ul':
        return node.querySelectorAll('li').length > 0 ?
        Array.from(node.children).
        map((li) => `- ${convertNode(li, level + 1).trim()}`).
        join('\n') + '\n\n' :
        '';
      case 'ol':
        return node.querySelectorAll('li').length > 0 ?
        Array.from(node.children).
        map((li, index) => `${index + 1}. ${convertNode(li, level + 1).trim()}`).
        join('\n') + '\n\n' :
        '';
      case 'li':
        if (node.getAttribute('data-type') === 'taskItem') {
          const checked = node.querySelector('input[type="checkbox"]')?.checked;
          return `- [${checked ? 'x' : ' '}] ${children}\n`;
        }
        return children;
      case 'a':
        const href = node.getAttribute('href') || '';
        return `[${children}](${href})`;
      case 'img':
        const src = node.getAttribute('src') || '';
        const alt = node.getAttribute('alt') || '';
        return `![${alt}](${src})`;
      case 'blockquote':
        return children.split('\n').
        map((line) => `> ${line}`).
        join('\n') + '\n\n';
      case 'table':
        const rows = Array.from(node.querySelectorAll('tr'));
        if (rows.length === 0) return '';
        const headers = Array.from(rows[0].querySelectorAll('th, td')).
        map((cell) => convertNode(cell, level).trim());
        const separator = headers.map(() => '---').join(' | ');
        const bodyRows = rows.slice(1).map((row) =>
        Array.from(row.querySelectorAll('td')).
        map((cell) => convertNode(cell, level).trim()).
        join(' | ')
        );
        return [
        headers.join(' | '),
        separator,
        ...bodyRows].
        join('\n') + '\n\n';
      case 'th':
      case 'td':
        return children;
      case 'hr':
        return '---\n\n';
      case 'br':
        return '\n';
      case 'mark':
        return `==${children}==`;
      // Custom elements
      case 'span':
        if (node.classList.contains('question-hint')) {
          return `💡 **Hint:** ${children}`;
        }
        if (node.classList.contains('correct-answer')) {
          return `✓ **Correct Answer:** ${children}`;
        }
        if (node.classList.contains('math-inline') || node.classList.contains('math-block')) {
          const latex = node.getAttribute('data-latex') || '';
          const isBlock = node.classList.contains('math-block');
          return isBlock ? `$$\n${latex}\n$$\n\n` : `$${latex}$`;
        }
        return children;
      case 'div':
        if (node.classList.contains('explanation-block')) {
          return `> **Explanation:**\n> ${children.split('\n').join('\n> ')}\n\n`;
        }
        if (node.classList.contains('math-block')) {
          const latex = node.getAttribute('data-latex') || '';
          return `$$\n${latex}\n$$\n\n`;
        }
        return children;
      default:
        return children;
    }
  };
  // Convert all top-level nodes
  Array.from(div.childNodes).forEach((node) => {
    markdown += convertNode(node);
  });
  // Clean up extra newlines
  return markdown.replace(/\n{3,}/g, '\n\n').trim();
};
// Export as different formats
export const exportContent = (format, content, filename = 'document') => {
  let data, mimeType, extension;
  switch (format) {
    case 'html':
      data = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${filename}</title>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
    code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
    pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
    .question-hint { background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }
    .correct-answer { background: #d4edda; padding: 10px; border-left: 4px solid #28a745; margin: 10px 0; font-weight: bold; }
    .explanation-block { background: #d1ecf1; padding: 10px; border-left: 4px solid #17a2b8; margin: 10px 0; }
  </style>
</head>
<body>
${content}
</body>
</html>`;
      mimeType = 'text/html';
      extension = 'html';
      break;
    case 'markdown':
      data = content;
      mimeType = 'text/markdown';
      extension = 'md';
      break;
    case 'json':
      data = content;
      mimeType = 'application/json';
      extension = 'json';
      break;
    default:
      data = content;
      mimeType = 'text/plain';
      extension = 'txt';
  }
  // Create blob and download
  const blob = new Blob([data], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}.${extension}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};