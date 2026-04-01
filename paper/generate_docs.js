'use strict';
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, ExternalHyperlink
} = require('docx');
const fs = require('fs');
const path = require('path');

// ─── Helpers ───────────────────────────────────────────────────────────────

const border = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
const cellBorders = { top: border, bottom: border, left: border, right: border };

function normalBorder() {
  return { top: border, bottom: border, left: border, right: border };
}

/** Make a plain body paragraph with APA-style double spacing */
function bodyParagraph(runs, opts = {}) {
  return new Paragraph({
    spacing: { line: 480, lineRule: 'auto', before: 0, after: 0 },
    alignment: AlignmentType.LEFT,
    ...opts,
    children: runs
  });
}

/** Render a chunk of inline markdown text into TextRun array.
 *  Handles **bold**, *italic*, hyperlinks embedded in text.
 */
function parseInline(text) {
  // We process bold (**...**) and italic (*...*) and links [text](url)
  const runs = [];
  // Use a simple state machine
  let i = 0;
  let cur = '';
  while (i < text.length) {
    // Check for **bold**
    if (text[i] === '*' && text[i + 1] === '*') {
      if (cur) { runs.push(new TextRun({ text: cur, font: 'Times New Roman', size: 24 })); cur = ''; }
      i += 2;
      let end = text.indexOf('**', i);
      if (end === -1) end = text.length;
      runs.push(new TextRun({ text: text.slice(i, end), bold: true, font: 'Times New Roman', size: 24 }));
      i = end + 2;
    }
    // Check for *italic* (but not **)
    else if (text[i] === '*' && text[i + 1] !== '*') {
      if (cur) { runs.push(new TextRun({ text: cur, font: 'Times New Roman', size: 24 })); cur = ''; }
      i += 1;
      let end = text.indexOf('*', i);
      if (end === -1) end = text.length;
      runs.push(new TextRun({ text: text.slice(i, end), italics: true, font: 'Times New Roman', size: 24 }));
      i = end + 1;
    }
    // Check for [text](url)
    else if (text[i] === '[') {
      if (cur) { runs.push(new TextRun({ text: cur, font: 'Times New Roman', size: 24 })); cur = ''; }
      const closeBracket = text.indexOf(']', i);
      if (closeBracket !== -1 && text[closeBracket + 1] === '(') {
        const closeParen = text.indexOf(')', closeBracket);
        if (closeParen !== -1) {
          const linkText = text.slice(i + 1, closeBracket);
          const linkUrl = text.slice(closeBracket + 2, closeParen);
          runs.push(new TextRun({ text: linkText, font: 'Times New Roman', size: 24, color: '0563C1', underline: { type: 'single' } }));
          i = closeParen + 1;
        } else { cur += text[i]; i++; }
      } else { cur += text[i]; i++; }
    } else {
      cur += text[i];
      i++;
    }
  }
  if (cur) { runs.push(new TextRun({ text: cur, font: 'Times New Roman', size: 24 })); }
  if (runs.length === 0) runs.push(new TextRun({ text: '', font: 'Times New Roman', size: 24 }));
  return runs;
}

/** Convert a markdown paragraph line to a Paragraph element */
function mdLineToParagraph(line, isRef = false) {
  // Indent for hanging reference style
  const spacing = { line: 480, lineRule: 'auto', before: 0, after: 0 };
  const indent = isRef ? { left: 720, hanging: 720 } : undefined;
  return new Paragraph({
    spacing,
    alignment: AlignmentType.LEFT,
    indent,
    children: parseInline(line)
  });
}

/** Make an H1 paragraph */
function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 480, after: 240 },
    children: [new TextRun({ text, font: 'Times New Roman', size: 28, bold: true })]
  });
}

/** Make an H2 paragraph */
function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 360, after: 180 },
    children: [new TextRun({ text, font: 'Times New Roman', size: 26, bold: true, italics: true })]
  });
}

/** Empty line spacer */
function emptyLine() {
  return new Paragraph({
    spacing: { line: 480, lineRule: 'auto', before: 0, after: 0 },
    children: [new TextRun({ text: '', font: 'Times New Roman', size: 24 })]
  });
}

// ─── Table builders ────────────────────────────────────────────────────────

function makeTable1() {
  // Table 1: Experimental conditions
  // Columns: Condition | σ₀ | Tax policy | Network | Floor
  const colWidths = [1600, 800, 2000, 1960, 1000]; // total = 7360 (fits in 9360 margin)
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  const headerBg = 'D5E8F0';

  const headers = ['Condition', '\u03C3\u2080', 'Tax policy', 'Network', 'Floor'];
  const rows = [
    ['ineq_low', '0.3', 'progressive', 'small_world', 'No'],
    ['ineq_medium', '0.8', 'progressive', 'small_world', 'No'],
    ['ineq_high', '1.5', 'progressive', 'small_world', 'No'],
    ['tax_none', '0.8', 'none', 'small_world', 'No'],
    ['tax_flat', '0.8', 'flat', 'small_world', 'No'],
    ['tax_progressive', '0.8', 'progressive', 'small_world', 'No'],
    ['net_none', '0.8', 'progressive', 'none', 'No'],
    ['net_small_world', '0.8', 'progressive', 'small_world', 'No'],
    ['net_scale_free', '0.8', 'progressive', 'scale_free', 'No'],
    ['floor_off', '0.8', 'progressive', 'small_world', 'No'],
    ['floor_on', '0.8', 'progressive', 'small_world', 'Yes'],
  ];

  const makeCell = (text, isHeader = false, w = 1600) =>
    new TableCell({
      borders: normalBorder(),
      width: { size: w, type: WidthType.DXA },
      shading: isHeader ? { fill: headerBg, type: ShadingType.CLEAR } : { fill: 'FFFFFF', type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({
        spacing: { line: 240, lineRule: 'auto' },
        children: [new TextRun({ text, font: 'Times New Roman', size: 22, bold: isHeader })]
      })]
    });

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => makeCell(h, true, colWidths[i]))
      }),
      ...rows.map(row =>
        new TableRow({
          children: row.map((cell, i) => makeCell(cell, false, colWidths[i]))
        })
      )
    ]
  });
}

function makeTable2() {
  // Table 2: Final-step outcome metrics
  // Columns: Condition | Gini | Mean Wealth | Total Wealth | Upper Class | Lower Class | Mean Reputation | Clustering
  const colWidths = [1500, 700, 1200, 1300, 1100, 1100, 1600, 1100]; // total = 9600 -> adjust to 9360
  // Recalculate to sum to 9360
  const adjusted = [1460, 700, 1160, 1260, 1060, 1060, 1500, 1160]; // sum = 9360
  const totalWidth = adjusted.reduce((a, b) => a + b, 0);
  const headerBg = 'D5E8F0';

  const headers = ['Condition', 'Gini', 'Mean Wealth', 'Total Wealth', 'Upper Class', 'Lower Class', 'Mean Reputation', 'Clustering'];
  const rows = [
    ['ineq_low', '0.362', '0.436', '43.61', '0.254', '0.333', '1.001', '0.382'],
    ['ineq_medium', '0.378', '0.714', '71.40', '0.291', '0.343', '0.902', '0.382'],
    ['ineq_high', '0.185*', '11.888*', '1188.84*', '0.133', '0.150', '0.825', '0.382'],
    ['tax_none', '0.436', '1.900', '189.95', '0.256', '0.336', '0.970', '0.382'],
    ['tax_flat', '0.383', '0.690', '69.03', '0.286', '0.350', '0.893', '0.382'],
    ['tax_progressive', '0.378', '0.714', '71.40', '0.291', '0.343', '0.902', '0.382'],
    ['net_none', '0.383', '0.693', '69.25', '0.277', '0.349', '0.899', '0.000'],
    ['net_scale_free', '0.377*', '0.710', '70.96', '0.298', '0.343', '0.894', '0.123'],
    ['net_small_world', '0.378', '0.714', '71.40', '0.291', '0.343', '0.902', '0.382'],
    ['floor_off', '0.378', '0.714', '71.40', '0.291', '0.343', '0.902', '0.382'],
    ['floor_on', '0.391', '0.443', '44.34', '0.316', '0.354', '0.847*', '0.382'],
  ];

  const makeCell = (text, isHeader = false, w = 700, bold = false) =>
    new TableCell({
      borders: normalBorder(),
      width: { size: w, type: WidthType.DXA },
      shading: isHeader ? { fill: headerBg, type: ShadingType.CLEAR } : { fill: 'FFFFFF', type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 80, right: 80 },
      verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({
        spacing: { line: 240, lineRule: 'auto' },
        alignment: isHeader ? AlignmentType.CENTER : AlignmentType.RIGHT,
        children: [new TextRun({ text, font: 'Times New Roman', size: 20, bold: isHeader || bold })]
      })]
    });

  // First column left-aligned
  const makeCellLeft = (text, isHeader = false, w = 1460) =>
    new TableCell({
      borders: normalBorder(),
      width: { size: w, type: WidthType.DXA },
      shading: isHeader ? { fill: headerBg, type: ShadingType.CLEAR } : { fill: 'FFFFFF', type: ShadingType.CLEAR },
      margins: { top: 60, bottom: 60, left: 80, right: 80 },
      verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({
        spacing: { line: 240, lineRule: 'auto' },
        alignment: AlignmentType.LEFT,
        children: [new TextRun({ text, font: 'Times New Roman', size: 20, bold: isHeader })]
      })]
    });

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: adjusted,
    rows: [
      new TableRow({
        tableHeader: true,
        children: [
          makeCellLeft(headers[0], true, adjusted[0]),
          ...headers.slice(1).map((h, i) => makeCell(h, true, adjusted[i + 1]))
        ]
      }),
      ...rows.map(row =>
        new TableRow({
          children: [
            makeCellLeft(row[0], false, adjusted[0]),
            ...row.slice(1).map((cell, i) => makeCell(cell, false, adjusted[i + 1]))
          ]
        })
      )
    ]
  });
}

// ─── Shared styles config ──────────────────────────────────────────────────

function buildStyles() {
  return {
    default: {
      document: {
        run: { font: 'Times New Roman', size: 24 }
      }
    },
    paragraphStyles: [
      {
        id: 'Heading1',
        name: 'Heading 1',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 28, bold: true, font: 'Times New Roman', color: '000000' },
        paragraph: { spacing: { before: 480, after: 240 }, outlineLevel: 0 }
      },
      {
        id: 'Heading2',
        name: 'Heading 2',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 26, bold: true, italics: true, font: 'Times New Roman', color: '000000' },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 1 }
      }
    ]
  };
}

// ─── Build manuscript_anon.docx ────────────────────────────────────────────

function buildAnonDoc() {
  const children = [];

  // Title
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { line: 480, lineRule: 'auto', before: 0, after: 360 },
    children: [new TextRun({
      text: 'Emergent Wealth Inequality in Agent-Based Civilizations: Effects of Fiscal Policy, Network Topology, and Initial Conditions',
      bold: true,
      font: 'Times New Roman',
      size: 32
    })]
  }));

  // Abstract section
  children.push(heading1('Abstract'));

  const abstractText = 'Agent-based modeling offers a powerful framework for studying emergent social phenomena from individual-level interactions. This paper presents Civilization-ABM, an open-source computational model of an artificial society in which heterogeneous agents interact through economic exchange, social network ties, and institutional rules. Three factors are systematically varied across 11 experimental conditions: initial wealth dispersion, fiscal redistribution policy, and social network topology. Experiments use 30 replications per condition over 200 simulation steps (N = 100 agents; 66,000 total simulation runs).';

  const abstractText2 = 'Four principal findings emerge. Progressive taxation reduces the Gini coefficient by 13.3% relative to the no-taxation baseline, but at a cost of 62.5% of aggregate wealth \u2014 a computational confirmation of the equity\u2013efficiency trade-off. High initial wealth dispersion (\u03C3 = 1.5) paradoxically produces the lowest final inequality of all conditions tested (Gini = 0.185), 51% below the medium-dispersion baseline, through a redistribution amplification mechanism in which greater absolute wealth activates progressive tax brackets more intensively. Social network topology exerts only modest inequality effects (\u0394Gini < 0.006). A minimum wealth floor policy counterproductively increases inequality (+3.5% Gini) while reducing total wealth by 37.8%, revealing an adverse interaction with progressive redistribution.';

  const abstractText3 = 'Model code and data are available at https://github.com/jmdelaserna/civilization-abm.';

  children.push(mdLineToParagraph(abstractText));
  children.push(emptyLine());
  children.push(mdLineToParagraph(abstractText2));
  children.push(emptyLine());
  children.push(mdLineToParagraph(abstractText3));
  children.push(emptyLine());

  // Keywords
  children.push(new Paragraph({
    spacing: { line: 480, lineRule: 'auto', before: 0, after: 0 },
    children: [
      new TextRun({ text: 'Keywords: ', bold: true, font: 'Times New Roman', size: 24 }),
      new TextRun({ text: 'agent-based modeling; wealth inequality; fiscal policy; social networks; Gini coefficient; emergence', font: 'Times New Roman', size: 24 })
    ]
  }));
  children.push(emptyLine());

  // ── Introduction ──
  children.push(heading1('Introduction'));

  const introParas = [
    'The study of social inequality has occupied sociologists, economists, and political scientists for centuries, yet a fundamental challenge persists: how do macro-level patterns of wealth concentration emerge from micro-level individual decisions and interactions? Traditional analytical approaches \u2014 equilibrium models, regression analyses, survey-based methods \u2014 are powerful but structurally limited in their capacity to capture the dynamic, nonlinear, and emergent nature of social stratification (Piketty & Saez, 2014; Atkinson, 2015). Agent-based modeling (ABM) offers a complementary paradigm: rather than deriving macro-patterns from assumed equilibria, it *grows* them from the bottom up, allowing researchers to observe how systemic inequality emerges from the repeated interaction of heterogeneous autonomous agents (Epstein & Axtell, 1996).',
    'The seminal contribution of Epstein and Axtell (1996), who introduced the Sugarscape model, demonstrated that persistent and highly skewed wealth distributions could emerge spontaneously from a population of agents following elementary rules in a resource-heterogeneous environment, without any design intent or central authority. This generative approach to social science (Epstein, 2006) has since been extended to study segregation (Schelling, 1971), cooperation (Axelrod, 1984), market dynamics (Tesfatsion & Judd, 2006), epidemiological spread (Epstein, 2009), and political conflict (Cederman, 1997). However, a systematic computational study that integrates fiscal policy mechanisms, dynamic social class formation, and network-mediated interaction within a single unified artificial civilization model remains underexplored.',
    'The question of what drives wealth inequality is not merely academic. Global inequality has risen substantially over the past four decades (Atkinson et al., 2011), with the top 1% of households capturing an increasingly disproportionate share of total wealth in both developed and developing economies (Piketty, 2014). Piketty\'s empirical analysis suggests that when the rate of return on capital exceeds economic growth, wealth concentration becomes self-reinforcing. Parallel work in econophysics has demonstrated that even in the simplest closed economic systems \u2014 where agents exchange random amounts of money \u2014 the stationary distribution converges to a Boltzmann-Gibbs exponential law, implying that inequality is not an aberration but a natural thermodynamic outcome of economic exchange (Dragulescu & Yakovenko, 2000). Whether institutional interventions such as progressive taxation can meaningfully alter this trajectory is an empirical question that ABM is uniquely suited to address.',
    'Social network structure adds a further dimension of complexity. Real human societies exhibit the "small-world" property \u2014 high local clustering combined with short global path lengths \u2014 first formalized by Watts and Strogatz (1998). They also show scale-free degree distributions characteristic of preferential attachment (Barab\u00E1si & Albert, 1999), meaning that highly connected individuals disproportionately influence resource and status flows. The topology of these networks has been shown to modulate the spread of inequality (Brzezinski & Kania, 2025), the emergence of cooperation (Nowak & May, 1992), and the resilience of social institutions (Ostrom, 1990). Yet the joint effect of network topology and fiscal policy on wealth dynamics has not been systematically examined within an ABM framework.',
    'This paper makes three contributions. First, it introduces Civilization-ABM, an open-source, reproducible, Mesa-based (Kazil et al., 2020) simulation platform integrating economic exchange, dynamic social class formation, reputation mechanisms, institutional rules, and NetworkX-based social graphs in a unified modular architecture. Second, it reports a systematic factorial experiment across 11 conditions, varying initial inequality, fiscal policy, and network topology, with 30 replications per condition. Third, it reports and interprets emergent macro-level outcomes \u2014 Gini coefficient, Theil index, Palma ratio, class mobility, and reputational dynamics \u2014 against predictions from econophysics, institutional economics, and complexity science.',
  ];

  for (const para of introParas) {
    children.push(mdLineToParagraph(para));
    children.push(emptyLine());
  }

  // ── Theoretical Framework ──
  children.push(heading1('Theoretical Framework and Related Work'));

  children.push(heading2('Agent-Based Modeling and the Generative Approach'));
  const tfParas = [
    'Agent-based modeling is a computational methodology in which a system is represented as a collection of autonomous agents \u2014 each with its own attributes, rules, and memory \u2014 that interact with each other and with a shared environment (Gilbert & Troitzsch, 2005; Tesfatsion & Judd, 2006). Unlike top-down analytical models, ABM is bottom-up: macro-level phenomena emerge from the aggregate of micro-level behaviors (Epstein & Axtell, 1996). This generative epistemology, formalized by Epstein (2008) under the motto "if you didn\'t grow it, you didn\'t explain it," has become a foundational principle of computational social science.',
    'The canonical wealth-distribution ABM dates to Sugarscape (Epstein & Axtell, 1996), in which agents harvest and accumulate a resource distributed unevenly across a landscape. Despite each agent following only simple local rules, the emergent wealth distribution closely resembles empirically observed Pareto distributions. Subsequent extensions introduced trade, disease transmission, cultural evolution (Axelrod, 1997), and combat (Epstein, 1999), demonstrating ABM\'s versatility as a platform for social theorizing.',
  ];
  for (const para of tfParas) {
    children.push(mdLineToParagraph(para));
    children.push(emptyLine());
  }

  children.push(heading2('Econophysics of Wealth Distribution'));
  const ecoParas = [
    'An important theoretical benchmark is provided by the econophysics literature. Dragulescu and Yakovenko (2000) showed that in any closed economic system where agents exchange random amounts of money in pairwise transactions, the equilibrium money distribution is a Boltzmann-Gibbs exponential, where T is the "economic temperature" (mean money per agent). This result implies that without redistribution mechanisms, inequality is a thermodynamic inevitability. Models incorporating capital returns and savings propensities generate Pareto power-law tails (Yakovenko & Rosser, 2009), consistent with empirical data on the ultra-rich. These theoretical results provide the null hypothesis for our experiments: without taxation, Civilization-ABM should converge toward a highly unequal stationary distribution.',
  ];
  for (const para of ecoParas) {
    children.push(mdLineToParagraph(para));
    children.push(emptyLine());
  }

  children.push(heading2('Fiscal Policy and Redistribution'));
  const fiscalParas = [
    'The impact of redistribution on inequality has been studied extensively in both empirical economics (Piketty, 2014; Milanovic, 2016) and computational models (Fagiolo & Roventini, 2017). Progressive taxation \u2014 where marginal rates increase with wealth \u2014 is theoretically predicted to compress the wealth distribution more effectively than flat-rate taxation (Atkinson et al., 2011). However, redistribution entails trade-offs: aggressive taxation may reduce incentives for wealth accumulation, potentially shrinking the total resource pool. This paper extends this line of inquiry by comparing no taxation, flat taxation, and progressive taxation within the same computational framework.',
  ];
  for (const para of fiscalParas) {
    children.push(mdLineToParagraph(para));
    children.push(emptyLine());
  }

  children.push(heading2('Social Networks and Inequality'));
  const netParas = [
    'Watts and Strogatz (1998) demonstrated that a small amount of random rewiring in a regular network creates small-world properties. Barab\u00E1si and Albert (1999) showed that preferential attachment generates scale-free degree distributions, in which hubs may concentrate wealth through disproportionate interaction. Recent agent-based work calibrated to Italian wealth survey data confirmed that network-mediated interaction explains a substantial portion of observed wealth persistence (Brzezinski & Kania, 2025). This paper tests whether these effects persist when strong fiscal institutions are simultaneously present.',
  ];
  for (const para of netParas) {
    children.push(mdLineToParagraph(para));
    children.push(emptyLine());
  }

  children.push(heading2('Social Class Dynamics, Mobility, and Norms'));
  const classParas = [
    'Social stratification has been modeled computationally since Schelling\'s (1971) landmark work on residential segregation. In this model, social classes emerge endogenously as a function of each agent\'s wealth relative to the population mean, aligning with the sociological tradition of relative deprivation theory (Runciman, 1966) and the economic literature on intergenerational mobility (Chetty et al., 2014). Beyond economic exchange, normative mechanisms \u2014 reputation, sanctioning, ostracism \u2014 regulate behavior and sustain cooperation (Fehr & G\u00E4chter, 2002). This model incorporates reputation as an agent attribute that decays under competitive exploitation and recovers through cooperative transfers, drawing on Axelrod\'s (1984) evolutionary cooperation framework.',
  ];
  for (const para of classParas) {
    children.push(mdLineToParagraph(para));
    children.push(emptyLine());
  }

  // ── Methods ──
  children.push(heading1('Methods'));

  children.push(heading2('Model Overview'));
  children.push(mdLineToParagraph('Civilization-ABM is implemented in Python 3.11 using the Mesa 3.x agent-based modeling framework (Kazil et al., 2020). Full source code, experimental configurations, and analysis scripts are available at https://github.com/jmdelaserna/civilization-abm under an MIT license, and the simulation model is deposited at the CoMSES Computational Model Library. The model comprises four tightly coupled modules: (1) agents, (2) social network environment, (3) institutional rules, and (4) data collection.'));
  children.push(emptyLine());

  children.push(heading2('Agents'));
  children.push(mdLineToParagraph('Each simulation contains N = 100 agents. Upon initialization, each agent is assigned: wealth (w) drawn from a log-normal distribution LN(\u03BC = 2.3, \u03C3 = \u03C3\u2080), where \u03C3\u2080 is the initial inequality parameter; strategy (s) drawn uniformly from {cooperative, competitive, neutral}; and reputation (r) initialized at 1.0 (range: 0.0\u20132.0). Social class (c) is dynamically assigned at each step as lower (w < 0.5\u03BC\u0305), middle (0.5\u03BC\u0305 \u2264 w < 1.5\u03BC\u0305), or upper (w \u2265 1.5\u03BC\u0305), where \u03BC\u0305 is the current population mean wealth.'));
  children.push(emptyLine());
  children.push(mdLineToParagraph('At each simulation step, agents are activated in random order. Each activated agent selects a random other agent and executes a strategy-dependent wealth transfer: cooperative agents donate 5% of own wealth to poorer agents (reputation +0.02); competitive agents extract wealth from richer agents (other\'s reputation \u22120.05); neutral agents transfer 2.5% with probability 0.5.'));
  children.push(emptyLine());

  children.push(heading2('Social Network'));
  children.push(mdLineToParagraph('Three network conditions are implemented using NetworkX (Hagberg et al., 2008): no network (fully random interaction); small-world (Watts-Strogatz graph with k = 4 and p = 0.1; Watts & Strogatz, 1998); and scale-free (Barab\u00E1si-Albert graph with m = 2; Barab\u00E1si & Albert, 1999).'));
  children.push(emptyLine());

  children.push(heading2('Institutional Rules'));
  children.push(mdLineToParagraph('Three fiscal conditions are applied at the end of each step: no taxation; flat tax (5% collected from each agent, redistributed equally); and progressive tax (marginal rates of 5% for w \u2264 20, 10% for 20 < w \u2264 50, 20% for w > 50; proceeds redistributed equally). Agents with reputation r < 0.3 incur a wealth penalty of 0.5 units per step. An optional minimum wealth floor maintains w \u2265 1.0 for all agents.'));
  children.push(emptyLine());

  children.push(heading2('Experimental Design'));
  children.push(mdLineToParagraph('A single-factor design is implemented across 11 conditions (Table 1), varying one independent variable at a time against a common baseline. Each condition runs for 30 independent replications with 200 simulation steps (seeds = 42, 43, \u2026, 71).'));
  children.push(emptyLine());

  // Table 1 caption
  children.push(new Paragraph({
    spacing: { line: 480, lineRule: 'auto', before: 240, after: 120 },
    children: [
      new TextRun({ text: 'Table 1', bold: true, italics: false, font: 'Times New Roman', size: 24 }),
      new TextRun({ text: '\nNote.', italics: true, font: 'Times New Roman', size: 24 }),
      new TextRun({ text: ' Experimental conditions.', font: 'Times New Roman', size: 24 })
    ]
  }));
  children.push(makeTable1());
  children.push(emptyLine());

  children.push(heading2('Outcome Measures'));
  children.push(mdLineToParagraph('The following metrics are computed at each step and averaged across 30 replications: Gini coefficient (Gini, 1921); Theil index T (Theil, 1967); Palma ratio (Palma, 2011); mean and total wealth; upper and lower class fractions; mean reputation; and network clustering coefficient.'));
  children.push(emptyLine());

  // ── Results ──
  children.push(heading1('Results'));

  children.push(heading2('Baseline Dynamics'));
  children.push(mdLineToParagraph('A representative single simulation under baseline conditions (N = 100, \u03C3\u2080 = 0.8, progressive tax, small-world network, seed = 42) converged after 200 steps to a Gini coefficient of 0.336 and a strategy entropy of 1.580 bits \u2014 approaching the theoretical maximum for three strategies (log\u2082 3 = 1.585 bits), indicating sustained behavioral diversity with no dominant strategy, consistent with evolutionary game-theoretic predictions (Axelrod, 1984). The baseline Gini falls within the empirically observed range for mixed-economy European nations, providing an initial plausibility check for the model. The full systematic results are summarized in Table 2.'));
  children.push(emptyLine());

  // Table 2 caption
  children.push(new Paragraph({
    spacing: { line: 480, lineRule: 'auto', before: 240, after: 120 },
    children: [
      new TextRun({ text: 'Table 2', bold: true, font: 'Times New Roman', size: 24 }),
      new TextRun({ text: '\nNote.', italics: true, font: 'Times New Roman', size: 24 }),
      new TextRun({ text: ' Final-step outcome metrics averaged across 30 replications per condition. Asterisk (*) indicates notable values discussed in text.', font: 'Times New Roman', size: 24 })
    ]
  }));
  children.push(makeTable2());
  children.push(emptyLine());

  children.push(heading2('Effect of Fiscal Policy'));
  children.push(mdLineToParagraph('The no-taxation condition produced the highest Gini coefficient (0.436), consistent with econophysics predictions that unconstrained exchange converges toward highly skewed distributions (Dragulescu & Yakovenko, 2000). Progressive taxation reduced inequality to Gini = 0.378 \u2014 a 13.3% reduction \u2014 marginally outperforming flat taxation (Gini = 0.383). Both redistribution conditions entailed substantial aggregate wealth costs: total wealth under progressive taxation (71.4 units) represented only 37.6% of the no-tax baseline (189.9 units), confirming computationally the classical equity\u2013efficiency trade-off (Atkinson et al., 2011; Piketty, 2014). Figure 1 shows the temporal evolution of the Gini coefficient across the three policy conditions.'));
  children.push(emptyLine());

  children.push(heading2('Effect of Initial Wealth Dispersion \u2014 The Redistribution Amplification Paradox'));
  children.push(mdLineToParagraph('The most striking result emerged from the initial inequality experiment. Contrary to the prediction that greater initial inequality produces greater final inequality, the high-dispersion condition (\u03C3 = 1.5) converged to the lowest Gini of all eleven conditions: 0.185 \u2014 a value 51.0% below the medium-dispersion baseline and 57.5% below the no-tax condition. Mean wealth under ineq_high (11.888 units) was 16.6 times greater than under ineq_medium (0.714 units), and total wealth 16.6-fold higher. This wealth amplification activates the progressive tax brackets more aggressively, producing much larger absolute transfers that substantially compress the distribution. We term this phenomenon the redistribution amplification effect: in models with progressive institutional redistribution, high initial wealth dispersion can paradoxically produce lower equilibrium inequality than moderate initial dispersion, because absolute wealth levels determine the intensity of redistribution independently of relative dispersion. Figure 2 illustrates this paradox.'));
  children.push(emptyLine());

  children.push(heading2('Effect of Social Network Topology'));
  children.push(mdLineToParagraph('Network topology exerted the smallest effect of all three experimental factors. Gini coefficients ranged from 0.377 (scale-free) to 0.383 (no network) \u2014 a spread of only 0.006, representing a 1.6% difference. The no-network condition produced the highest inequality, indicating that network-mediated interaction consistently reduces inequality regardless of topology. Scale-free networks produced marginally lower inequality than small-world networks, contrary to theoretical predictions that hub-dominated networks concentrate wealth (Barab\u00E1si & Albert, 1999; Brzezinski & Kania, 2025). This may be because hub agents participate more frequently in cooperative transfers, partially offsetting hub-mediated concentration.'));
  children.push(emptyLine());

  children.push(heading2('Effect of Minimum Wealth Floor \u2014 The Floor Policy Backfire'));
  children.push(mdLineToParagraph('The minimum wealth floor policy produced results opposite to its redistributive intent. Under floor_on, the Gini coefficient increased from 0.378 to 0.391 (+3.5%), total wealth fell by 37.8%, and mean reputation declined to 0.847 \u2014 the lowest value across all conditions. The floor simultaneously increased both upper-class and lower-class fractions, shrinking the middle class. This "polarization" pattern suggests that the floor mechanism disproportionately depletes middle-wealth agents, who contribute to floor maintenance but receive proportionally less redistribution benefit. Figure 3 illustrates the polarization effect.'));
  children.push(emptyLine());

  // ── Discussion ──
  children.push(heading1('Discussion'));

  children.push(heading2('Confirmation and Extension of Theoretical Predictions'));
  children.push(mdLineToParagraph('The baseline finding \u2014 unconstrained exchange produces a highly unequal distribution (Gini = 0.436) \u2014 is fully consistent with Dragulescu and Yakovenko\'s (2000) statistical mechanics prediction. Progressive taxation shifts the distribution toward greater equality, as predicted by redistribution theory (Piketty, 2014; Milanovic, 2016), but at a substantial aggregate cost \u2014 also as theoretically anticipated (Atkinson et al., 2011). The modest effect of network topology (\u0394Gini = 0.006) contrasts with studies reporting stronger network effects (Brzezinski & Kania, 2025; Nowak & May, 1992). This discrepancy may reflect a crowding-out effect: robust fiscal redistribution mechanisms may overshadow structural advantages conferred by network position. This suggests that network-based inequality interventions may be more effective in low-institution contexts than in environments with strong redistribution policies.'));
  children.push(emptyLine());

  children.push(heading2('The Redistribution Amplification Paradox'));
  children.push(mdLineToParagraph('The redistribution amplification effect \u2014 high initial dispersion producing lowest final inequality \u2014 has no precedent in standard equilibrium models of redistribution, where initial inequality typically propagates to final inequality unless strong corrective policies are applied. The mechanism is emergent: it arises from the interaction between log-normal wealth initialization, the progressive marginal tax schedule, and equal redistribution. The same institutional rule becomes far more powerful when operating on a wealth-rich environment. This finding resonates with an apparent paradox in development economics: societies with high initial wealth inequality but strong institutions sometimes achieve better distributional outcomes than those with low inequality but weak institutions (Milanovic, 2016). Our model offers a computational mechanism for this pattern.'));
  children.push(emptyLine());

  children.push(heading2('The Floor Policy Backfire Effect'));
  children.push(mdLineToParagraph('The counterproductive effect of the minimum wealth floor illustrates the general principle that institutional mechanisms can interact adversely when implemented simultaneously (Ostrom, 1990). The floor creates a "transfer trap" for middle-wealth agents: they contribute to floor maintenance but do not receive disproportionate benefit. This finding is relevant to debates about universal basic income and unconditional transfer programs: wealth floor policies combined with progressive taxation may create adverse interaction effects that are not visible when either mechanism is analyzed in isolation.'));
  children.push(emptyLine());

  children.push(heading2('Limitations and Future Directions'));
  children.push(mdLineToParagraph('Several limitations warrant acknowledgment. The model population is small (N = 100) and the simulation horizon short (200 steps), limiting exploration of long-run dynamics. Agent strategies are fixed and do not evolve; a natural extension would implement evolutionary dynamics (Axelrod, 1984; Nowak & May, 1992). The network is quasi-static; real social networks are far more dynamic, with tie formation driven by wealth similarity, reputation, and proximity. The model also excludes capital returns, credit, and inheritance \u2014 mechanisms identified as primary drivers of long-run wealth concentration (Piketty, 2014). Introducing spatial heterogeneity would allow examination of regional economic divergence (Chetty et al., 2014).'));
  children.push(emptyLine());

  // ── Conclusion ──
  children.push(heading1('Conclusion'));
  const conclusionParas = [
    'This paper presents Civilization-ABM, a systematic agent-based investigation of how initial conditions, fiscal institutions, and social network topology jointly shape the emergence of wealth inequality. Across 11 experimental conditions and 330 independent replications (66,000 total simulation runs), four principal findings emerge.',
    'Progressive redistribution reduces inequality at an efficiency cost. Progressive taxation achieved the lowest Gini among policy conditions (0.378), outperforming flat taxation (0.383) and no taxation (0.436), but at a 62.4% reduction in aggregate wealth, confirming the equity\u2013efficiency trade-off as a structurally robust feature of redistribution models.',
    'High initial wealth dispersion paradoxically minimizes final inequality. The high-dispersion condition (\u03C3 = 1.5) produced a final Gini of 0.185 \u2014 51% below the medium-dispersion baseline \u2014 through a redistribution amplification mechanism in which greater absolute wealth intensifies progressive tax extraction. This emergent result challenges the assumption that initial inequality predicts final inequality.',
    'Network topology is a secondary determinant of inequality. Gini variation across topology conditions was less than 0.006, suggesting that robust fiscal institutions overshadow network-structural effects.',
    'Floor policies can backfire when combined with progressive redistribution. Minimum wealth guarantees increased the Gini coefficient and reduced total wealth by hollowing out the middle class, underscoring the importance of modeling institutional combinations rather than individual policies in isolation.',
    'All model code, data, and experimental configurations are openly available at https://github.com/jmdelaserna/civilization-abm and at the CoMSES Computational Model Library.',
  ];
  for (const para of conclusionParas) {
    children.push(mdLineToParagraph(para));
    children.push(emptyLine());
  }

  // ── Acknowledgements ──
  children.push(heading1('Acknowledgements'));
  children.push(mdLineToParagraph('The author used Claude (Anthropic) for assistance with manuscript drafting and editorial revision. All scientific concepts, research design, computational model implementation, experimental execution, data analysis, and intellectual conclusions are entirely the author\'s own.'));
  children.push(emptyLine());

  // ── Author Contributions ──
  children.push(heading1('Author Contributions'));
  children.push(mdLineToParagraph('The author: Conceptualization, methodology, software, formal analysis, data curation, writing \u2014 original draft, writing \u2014 review and editing, visualization.'));
  children.push(emptyLine());

  // ── Statements and Declarations ──
  children.push(heading1('Statements and Declarations'));

  const statementsItems = [
    { label: 'Ethical considerations:', text: 'This study uses only computational simulation data. No human participants, human data, human tissue, or personal information of any kind were involved. Ethical approval was not required.' },
    { label: 'Consent to participate:', text: 'Not applicable. This study does not involve human participants.' },
    { label: 'Consent for publication:', text: 'Not applicable. This study does not contain data from any individual person.' },
    { label: 'Declaration of conflicting interest:', text: 'The author declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article.' },
    { label: 'Funding:', text: 'This research received no external funding. It was conducted independently using open-source computational tools.' },
    { label: 'Data availability:', text: 'All simulation code, experimental configurations, raw data, and figure-generation scripts are openly available at https://github.com/jmdelaserna/civilization-abm (MIT license) and at the CoMSES Computational Model Library. The dataset supporting the findings of this study (all_conditions.csv) is included in the repository.' },
  ];

  for (const item of statementsItems) {
    children.push(new Paragraph({
      spacing: { line: 480, lineRule: 'auto', before: 0, after: 0 },
      children: [
        new TextRun({ text: item.label + ' ', bold: true, font: 'Times New Roman', size: 24 }),
        new TextRun({ text: item.text, font: 'Times New Roman', size: 24 })
      ]
    }));
    children.push(emptyLine());
  }

  // ── References ──
  children.push(heading1('References'));

  const references = [
    'Atkinson, A. B. (2015). *Inequality: What can be done?* Harvard University Press.',
    'Atkinson, A. B., Piketty, T., & Saez, E. (2011). Top incomes in the long run of history. *Journal of Economic Literature*, *49*(1), 3\u201371.',
    'Axelrod, R. (1984). *The evolution of cooperation*. Basic Books.',
    'Axelrod, R. (1997). The dissemination of culture: A model with local convergence and global polarization. *Journal of Conflict Resolution*, *41*(2), 203\u2013226.',
    'Barab\u00E1si, A. L., & Albert, R. (1999). Emergence of scaling in random networks. *Science*, *286*(5439), 509\u2013512.',
    'Brzezinski, M., & Kania, A. (2025). Persistence of wealth inequality from network effects. *PLOS Complex Systems*. https://doi.org/10.1371/journal.pcsy.0000050',
    'Cederman, L. E. (1997). *Emergent actors in world politics*. Princeton University Press.',
    'Chetty, R., Hendren, N., Kline, P., & Saez, E. (2014). Where is the land of opportunity? The geography of intergenerational mobility in the United States. *Quarterly Journal of Economics*, *129*(4), 1553\u20131623.',
    'Dragulescu, A., & Yakovenko, V. M. (2000). Statistical mechanics of money. *European Physical Journal B*, *17*(4), 723\u2013729.',
    'Epstein, J. M. (1999). Agent-based computational models and generative social science. *Complexity*, *4*(5), 41\u201360.',
    'Epstein, J. M. (2006). *Generative social science: Studies in agent-based computational modeling*. Princeton University Press.',
    'Epstein, J. M. (2008). Why model? *Journal of Artificial Societies and Social Simulation*, *11*(4), 12. https://www.jasss.org/11/4/12.html',
    'Epstein, J. M. (2009). Modeling to contain pandemics. *Nature*, *460*(7256), 687.',
    'Epstein, J. M., & Axtell, R. (1996). *Growing artificial societies: Social science from the bottom up*. MIT Press.',
    'Fagiolo, G., & Roventini, A. (2017). Macroeconomic policy in DSGE and agent-based models Redux. *Journal of Artificial Societies and Social Simulation*, *20*(1), 1. https://www.jasss.org/20/1/1.html',
    'Fehr, E., & G\u00E4chter, S. (2002). Altruistic punishment in humans. *Nature*, *415*(6868), 137\u2013140.',
    'Gilbert, N., & Troitzsch, K. G. (2005). *Simulation for the social scientist* (2nd ed.). Open University Press.',
    'Gini, C. (1921). Measurement of inequality of incomes. *Economic Journal*, *31*(121), 124\u2013126.',
    'Grimm, V., Berger, U., Bastiansen, F., Eliassen, S., Ginot, V., Giske, J., & DeAngelis, D. L. (2006). A standard protocol for describing individual-based and agent-based models. *Ecological Modelling*, *198*(1\u20132), 115\u2013126.',
    'Hagberg, A. A., Schult, D. A., & Swart, P. J. (2008). Exploring network structure, dynamics, and function using NetworkX. In *Proceedings of the 7th Python in science conference (SciPy2008)* (pp. 11\u201315).',
    'Kazil, J., Masad, D., & Crooks, A. (2020). Utilizing Python for agent-based modeling: The Mesa framework. In *Social, cultural, and behavioral modeling (SBP-BRiMS 2020)*, Lecture Notes in Computer Science vol. 12268 (pp. 308\u2013317). Springer.',
    'Milanovic, B. (2016). *Global inequality: A new approach for the age of globalization*. Harvard University Press.',
    'Nowak, M. A., & May, R. M. (1992). Evolutionary games and spatial chaos. *Nature*, *359*(6398), 826\u2013829.',
    'Ostrom, E. (1990). *Governing the commons: The evolution of institutions for collective action*. Cambridge University Press.',
    'Palma, J. G. (2011). Homogeneous middles vs. heterogeneous tails, and the end of the "Inverted-U." *Development and Change*, *42*(1), 87\u2013153.',
    'Piketty, T. (2014). *Capital in the twenty-first century*. Harvard University Press.',
    'Piketty, T., & Saez, E. (2014). Inequality in the long run. *Science*, *344*(6186), 838\u2013843.',
    'Runciman, W. G. (1966). *Relative deprivation and social justice*. Routledge.',
    'Schelling, T. C. (1971). Dynamic models of segregation. *Journal of Mathematical Sociology*, *1*(2), 143\u2013186.',
    'Tesfatsion, L., & Judd, K. L. (Eds.). (2006). *Handbook of computational economics: Agent-based computational economics* (Vol. 2). Elsevier.',
    'Theil, H. (1967). *Economics and information theory*. North-Holland.',
    'Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of "small-world" networks. *Nature*, *393*(6684), 440\u2013442.',
    'Yakovenko, V. M., & Rosser, J. B. (2009). Colloquium: Statistical mechanics of money, wealth, and income. *Reviews of Modern Physics*, *81*(4), 1703\u20131725.',
  ];

  for (const ref of references) {
    children.push(new Paragraph({
      spacing: { line: 480, lineRule: 'auto', before: 0, after: 0 },
      indent: { left: 720, hanging: 720 },
      children: parseInline(ref)
    }));
  }

  const doc = new Document({
    styles: buildStyles(),
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children
    }]
  });

  return doc;
}

// ─── Build title_page.docx ─────────────────────────────────────────────────

function buildTitlePage() {
  const children = [];

  // Title
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { line: 480, lineRule: 'auto', before: 720, after: 480 },
    children: [new TextRun({
      text: 'Emergent Wealth Inequality in Agent-Based Civilizations: Effects of Fiscal Policy, Network Topology, and Initial Conditions',
      bold: true,
      font: 'Times New Roman',
      size: 32
    })]
  }));

  // Author info block
  const authorFields = [
    { label: 'Author:', value: 'Juan Mois\u00E9s de la Serna Tuya' },
    { label: 'Affiliation:', value: 'Universidad Internacional de La Rioja (UNIR), Spain' },
    { label: 'Postal address:', value: 'Av. de la Paz, 137, 26006 Logro\u00F1o, La Rioja, Spain' },
    { label: 'Phone:', value: '[to be added by author]' },
    { label: 'Email:', value: 'juanmoises.delaserna@unir.net' },
    { label: 'ORCID:', value: '0000-0002-8401-8018' },
  ];

  for (const field of authorFields) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { line: 480, lineRule: 'auto', before: 0, after: 0 },
      children: [
        new TextRun({ text: field.label + ' ', bold: true, font: 'Times New Roman', size: 24 }),
        new TextRun({ text: field.value, font: 'Times New Roman', size: 24 })
      ]
    }));
  }

  children.push(emptyLine());
  children.push(emptyLine());

  // Acknowledgements section
  children.push(new Paragraph({
    spacing: { line: 480, lineRule: 'auto', before: 240, after: 120 },
    children: [new TextRun({ text: 'Acknowledgements', bold: true, font: 'Times New Roman', size: 28 })]
  }));
  children.push(new Paragraph({
    spacing: { line: 480, lineRule: 'auto', before: 0, after: 0 },
    children: [new TextRun({ text: 'The author used Claude (Anthropic) for assistance with manuscript drafting and editorial revision. All scientific concepts, research design, computational model implementation, experimental execution, data analysis, and intellectual conclusions are entirely the author\'s own.', font: 'Times New Roman', size: 24 })]
  }));
  children.push(emptyLine());

  // Declarations
  const declarations = [
    {
      label: 'Declaration of conflicting interest:',
      text: 'The author declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article.'
    },
    {
      label: 'Funding statement:',
      text: 'This research received no external funding. It was conducted independently using open-source computational tools.'
    },
    {
      label: 'Ethical approval:',
      text: 'Not required. This study uses only computational simulation data. No human participants, human data, or human tissue were involved.'
    },
    {
      label: 'Consent to participate:',
      text: 'Not applicable.'
    },
    {
      label: 'Consent for publication:',
      text: 'Not applicable.'
    },
    {
      label: 'Data availability:',
      text: 'All simulation code, experimental configurations, raw data, and figure-generation scripts are openly available at https://github.com/jmdelaserna/civilization-abm (MIT license) and at the CoMSES Computational Model Library.'
    },
  ];

  for (const decl of declarations) {
    children.push(new Paragraph({
      spacing: { line: 480, lineRule: 'auto', before: 0, after: 0 },
      children: [
        new TextRun({ text: decl.label + ' ', bold: true, font: 'Times New Roman', size: 24 }),
        new TextRun({ text: decl.text, font: 'Times New Roman', size: 24 })
      ]
    }));
    children.push(emptyLine());
  }

  const doc = new Document({
    styles: buildStyles(),
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children
    }]
  });

  return doc;
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const paperDir = 'C:\\Users\\DELL\\Pictures\\Claude Industrial\\civilization-abm\\paper';

  console.log('Building manuscript_anon.docx...');
  const anonDoc = buildAnonDoc();
  const anonBuffer = await Packer.toBuffer(anonDoc);
  fs.writeFileSync(path.join(paperDir, 'manuscript_anon.docx'), anonBuffer);
  console.log('  Written: manuscript_anon.docx (' + anonBuffer.length + ' bytes)');

  console.log('Building title_page.docx...');
  const titleDoc = buildTitlePage();
  const titleBuffer = await Packer.toBuffer(titleDoc);
  fs.writeFileSync(path.join(paperDir, 'title_page.docx'), titleBuffer);
  console.log('  Written: title_page.docx (' + titleBuffer.length + ' bytes)');

  console.log('Done.');
}

main().catch(err => { console.error(err); process.exit(1); });
