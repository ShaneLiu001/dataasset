import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const outputDir = path.dirname(fileURLToPath(import.meta.url));
const sourcePath = path.resolve(outputDir, '..', 'Axure原型', '原型四步骤母版.svg');
const source = fs.readFileSync(sourcePath, 'utf8');

function extractBalancedGroup(input, startIndex) {
  const openPattern = /<g(?:\s[^>]*)?>/g;
  const closePattern = /<\/g>/g;
  openPattern.lastIndex = startIndex;
  const firstOpen = openPattern.exec(input);
  if (!firstOpen || firstOpen.index !== startIndex) {
    throw new Error(`Expected <g> at offset ${startIndex}`);
  }

  let depth = 1;
  let cursor = openPattern.lastIndex;
  while (depth > 0) {
    openPattern.lastIndex = cursor;
    closePattern.lastIndex = cursor;
    const nextOpen = openPattern.exec(input);
    const nextClose = closePattern.exec(input);
    if (!nextClose) throw new Error('Unclosed <g> element');

    if (nextOpen && nextOpen.index < nextClose.index) {
      depth += 1;
      cursor = openPattern.lastIndex;
    } else {
      depth -= 1;
      cursor = closePattern.lastIndex;
    }
  }

  return input.slice(startIndex, cursor);
}

function innerGroup(group) {
  return group.slice(group.indexOf('>') + 1, group.lastIndexOf('</g>'));
}

const style = source.match(/<style>[\s\S]*?<\/style>/)?.[0];
if (!style) throw new Error('SVG style block not found');

const blankStart = source.indexOf('<g id="blank-page">');
if (blankStart < 0) throw new Error('blank-page group not found');
const blankPage = innerGroup(extractBalancedGroup(source, blankStart));

const prefillStart = source.indexOf('<g id="prefill-result">');
if (prefillStart < 0) throw new Error('prefill-result group not found');
const prefillResult = innerGroup(extractBalancedGroup(source, prefillStart));

const steps = [
  { marker: '<!-- 步骤 1：打开工单 -->', file: '01_一键填充入口_Figma.svg', id: 'step-1-prefill-result', title: '步骤 1：打开工单查看预填结果' },
  { marker: '<!-- 步骤 2：核对待处理项 -->', file: '02_填充配置_Figma.svg', id: 'step-2-review-pending', title: '步骤 2：核对待处理项' },
  { marker: '<!-- 步骤 3：查看生成依据 -->', file: '03_生成中_Figma.svg', id: 'step-3-review-evidence', title: '步骤 3：查看生成依据' },
  { marker: '<!-- 步骤 4：确认提交 -->', file: '04_生成结果与依据_Figma.svg', id: 'step-4-confirm-submit', title: '步骤 4：确认提交' }
];

const fullSteps = [];

for (const [index, step] of steps.entries()) {
  const markerIndex = source.indexOf(step.marker);
  const groupStart = source.indexOf('<g ', markerIndex);
  if (markerIndex < 0 || groupStart < 0) throw new Error(`Step not found: ${step.title}`);

  const stepGroup = innerGroup(extractBalancedGroup(source, groupStart));
  const expanded = stepGroup
    .replace('<use href="#blank-page"/>', blankPage)
    .replace('<use href="#prefill-result"/>', prefillResult);
  const output = `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <title>${step.title}</title>
  <defs>
    ${style}
  </defs>
  <g id="${step.id}">
${expanded}
  </g>
</svg>
`;
  fs.writeFileSync(path.join(outputDir, step.file), output);
  fullSteps.push(`  <g id="${step.id}-full" transform="translate(${index * 1920} 0)">\n${expanded}\n  </g>`);
}

const fullOutput = `<svg xmlns="http://www.w3.org/2000/svg" width="7680" height="1080" viewBox="0 0 7680 1080">
  <title>数据资产盘点一键智能填充 - Figma 全流程画板</title>
  <defs>
    ${style}
  </defs>
${fullSteps.join('\n')}
</svg>
`;
fs.writeFileSync(path.join(outputDir, '00_全流程画板_Figma.svg'), fullOutput);

console.log(`Generated ${steps.length + 1} Figma SVG files in ${outputDir}`);
