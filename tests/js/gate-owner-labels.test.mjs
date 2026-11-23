#!/usr/bin/env node
/**
 * **Only the owner's (or a backup approver's) login counts for the gate's labels and overrides, and the gate is main's copy.**
 *
 * .github/workflows/gates.yml passes a PR on a human's word: `uat-passed`, `gate-override` with an `OVERRIDE:` comment,
 * and the owner's `uat:skip` on the issue (the no-UAT lane). Before kit 1.20 none of them checked who gave that word. Now
 * each counts only when the login that added it (the latest `labeled` event for it, or the event's sender while that
 * event is being handled) or wrote it is `product_owner_github` in haam.config.json on main, and never a bot; with no
 * owner there, nothing counts. Backup approvers (`backup_approvers_github`) count too. And the gate runs on
 * `pull_request_target`, so GitHub runs main's copy and a PR cannot rewrite the gate that judges it.
 *
 * These tests run the workflow's own github-script body, as written, against a fake `github` with synthetic logins.
 * Nothing reaches GitHub.
 *
 *   node --test tests/js/gate-owner-labels.test.mjs   (tests/test_workflows.py runs it with the Python suite)
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'template');
const KIT = path.resolve(ROOT, '..');
const GATES = fs.readFileSync(path.join(ROOT, '.github/workflows/gates.yml'), 'utf8');

/** The `script: |` block of the gate's github-script step, de-indented, exactly as the action runs it. */
function gateScript(text = GATES) {
  const lines = text.split('\n');
  const at = lines.findIndex((l) => /^\s+script: \|\s*$/.test(l));
  assert.ok(at >= 0, 'gates.yml has a github-script step');
  const indent = lines[at].search(/\S/);
  const body = [];
  for (const l of lines.slice(at + 1)) {
    if (l.trim() !== '' && l.search(/\S/) <= indent) break;
    body.push(l);
  }
  const min = Math.min(...body.filter((l) => l.trim()).map((l) => l.search(/\S/)));
  return body.map((l) => l.slice(min)).join('\n');
}
const AsyncFunction = (async () => {}).constructor;
const SCRIPT = gateScript();

const OWNER = { login: 'octo-owner', type: 'User' };
const AGENT = { login: 'octo-agent', type: 'User' };
const BACKUP = { login: 'octo-backup', type: 'User' };
const BOT = { login: 'github-actions[bot]', type: 'Bot' };
const CONFIG = { tracker: 'github', uat: 'owner-decides', product_owner_github: 'octo-owner', backup_approvers_github: ['octo-backup'], protected_paths: ['secret/**'] };

const labelled = (name, actor) => ({ event: 'labeled', label: { name }, actor });

/**
 * One run of the gate. [world]: the repository as the fake GitHub answers it; [event]: the event being handled.
 * Returns the release-gate statuses it posted, the labels and comments it added, its outputs and warnings.
 */
async function gate(world, event = {}, script = SCRIPT) {
  const w = {
    config: CONFIG, mainGates: GATES, files: { 7: ['src/a.ts'] }, comments: {}, events: {}, issues: {},
    prs: { 7: { number: 7, title: '#5: a change', head: { ref: '5-a-change', sha: 'f'.repeat(40) }, labels: [], draft: false, auto_merge: null } },
    ...world,
  };
  const calls = { statuses: [], added: [], comments: [], removed: [] };
  const labels = (pr) => pr.labels.map((name) => ({ name }));
  const notFound = () => Object.assign(new Error('Not Found'), { status: 404 });
  const rest = {
    repos: {
      getContent: async ({ path: file }) => {
        // main's own copy of gates.yml, which the PR's copy reads during the changeover.
        if (file === '.github/workflows/gates.yml') {
          if (w.mainGates === null) throw notFound();
          return { data: { content: Buffer.from(w.mainGates).toString('base64') } };
        }
        if (w.config === null) throw notFound();
        return { data: { content: Buffer.from(JSON.stringify(w.config)).toString('base64') } };
      },
      listCommitStatusesForRef: async () => ({ data: [] }),
      createCommitStatus: async (s) => { calls.statuses.push(s); return { data: {} }; },
    },
    pulls: {
      get: async ({ pull_number }) => ({ data: { ...w.prs[pull_number], labels: labels(w.prs[pull_number]) } }),
      list: async () => ({ data: Object.values(w.prs).map((pr) => ({ ...pr, labels: labels(pr) })) }),
      listFiles: async ({ pull_number }) => ({ data: (w.files[pull_number] ?? []).map((filename) => ({ filename })) }),
      listCommits: async () => ({ data: [] }),
    },
    issues: {
      get: async ({ issue_number }) => {
        const iss = w.issues[issue_number];
        if (!iss) throw notFound();
        return { data: { number: issue_number, state: 'open', ...iss, labels: iss.labels.map((name) => ({ name })) } };
      },
      listComments: async ({ issue_number }) => ({ data: w.comments[issue_number] ?? [] }),
      listEvents: async ({ issue_number }) => ({ data: w.events[issue_number] ?? [] }),
      addLabels: async (a) => { calls.added.push(a); return { data: {} }; },
      removeLabel: async (a) => { calls.removed.push(a); return { data: {} }; },
      createComment: async (a) => { calls.comments.push(a); return { data: {} }; },
    },
  };
  const github = { rest, paginate: async (fn, params) => (await fn(params)).data };
  const outputs = {};
  const warnings = [];
  const core = { info: () => {}, warning: (m) => warnings.push(m), setOutput: (k, v) => { outputs[k] = v; } };
  const context = {
    repo: { owner: 'octo', repo: 'repo' },
    eventName: event.eventName ?? 'pull_request_target',
    payload: { action: 'opened', pull_request: { number: 7 }, sender: OWNER, ...event.payload },
  };
  const process = { env: { REVIEW_MODE: '', CI_MODE: '', ...event.env } };
  await new AsyncFunction('github', 'context', 'core', 'process', script)(github, context, core, process);
  const status = calls.statuses.filter((s) => s.context === 'release-gate').at(-1);
  return { ...calls, status, outputs, warnings };
}

/** A world where PR #7 carries [labels], each added by the actor given. */
function withLabels(pairs, extra = {}) {
  return {
    prs: { 7: { number: 7, title: '#5: a change', head: { ref: '5-a-change', sha: 'f'.repeat(40) }, labels: pairs.map(([name]) => name), draft: false, auto_merge: null } },
    events: { 7: pairs.map(([name, actor]) => labelled(name, actor)) },
    ...extra,
  };
}

// ------------------------------------------------------------------------------------------------- AC1

test('AC1: uat-passed counts from the owner', async () => {
  const r = await gate(withLabels([['uat-passed', OWNER]]));
  assert.equal(r.status.state, 'success', r.status.description);
  assert.equal(r.status.description, 'UAT passed (label by @octo-owner)');
});

test('⛔ AC1: uat-passed added by another login or a bot does not count', async () => {
  for (const actor of [AGENT, BOT]) {
    const r = await gate(withLabels([['uat-passed', actor]]));
    assert.equal(r.status.state, 'failure', actor.login);
    assert.equal(r.status.description, `uat-passed was added by @${actor.login}, not the owner or a backup approver in haam.config.json: it doesn't count`, actor.login);
    assert.deepEqual(r.removed, [], 'the label is not removed: the owner decides what to do about it');
  }
});

test('AC1: uat-passed counts from a backup approver, and not when the config has no owner', async () => {
  const r = await gate(withLabels([['uat-passed', BACKUP]]));
  assert.equal(r.status.state, 'success', r.status.description);
  assert.equal(r.status.description, 'UAT passed (label by @octo-backup)');
  const none = await gate(withLabels([['uat-passed', BACKUP]], { config: { ...CONFIG, product_owner_github: '' } }));
  assert.equal(none.status.state, 'failure', 'backups alone, with no owner, are not an owner');
});

test('⛔ AC1: a bot is never the owner, even when the config names it', async () => {
  const r = await gate(withLabels([['uat-passed', BOT]], { config: { ...CONFIG, product_owner_github: 'github-actions[bot]' } }));
  assert.equal(r.status.state, 'failure');
});

test('⛔ AC1: the latest labeled event counts: the owner\'s label removed and added again by another login does not', async () => {
  const world = withLabels([['uat-passed', OWNER]]);
  world.events[7].push({ event: 'unlabeled', label: { name: 'uat-passed' }, actor: AGENT }, labelled('uat-passed', AGENT));
  const r = await gate(world);
  assert.equal(r.status.state, 'failure');
  assert.match(r.status.description, /@octo-agent/);
});

test('AC1: the login is compared without regard to case', async () => {
  const r = await gate(withLabels([['uat-passed', { login: 'Octo-Owner', type: 'User' }]]));
  assert.equal(r.status.state, 'success', r.status.description);
});

test('AC1: on the labeled event itself the sender counts, since the events API can lag behind it', async () => {
  const world = withLabels([['uat-passed', AGENT]]);
  world.events[7] = [];
  let r = await gate(world, { payload: { action: 'labeled', label: { name: 'uat-passed' }, sender: OWNER } });
  assert.equal(r.status.state, 'success', r.status.description);
  r = await gate(world, { payload: { action: 'labeled', label: { name: 'uat-passed' }, sender: AGENT } });
  assert.equal(r.status.state, 'failure');
});

// ------------------------------------------------------------------------------------------------- AC2

const override = (author, body = 'OVERRIDE: the owner tested it on the phone') => ({ body, user: author });

test('⛔ AC2: gate-override needs the owner\'s (or a backup\'s) label and OVERRIDE comment', async () => {
  const cases = [
    [OWNER, OWNER, 'success', 'Gate overridden by octo-owner'],
    [OWNER, AGENT, 'failure', 'OVERRIDE comment by @octo-agent doesn\'t count: only the owner\'s or a backup approver\'s does'],
    [BACKUP, BACKUP, 'success', 'Gate overridden by octo-backup'],
    [AGENT, OWNER, 'failure', 'gate-override was added by @octo-agent, not the owner or a backup approver in haam.config.json: it doesn\'t count'],
    [AGENT, AGENT, 'failure', 'gate-override was added by @octo-agent, not the owner or a backup approver in haam.config.json: it doesn\'t count'],
  ];
  for (const [labeller, author, state, description] of cases) {
    const r = await gate(withLabels([['gate-override', labeller]], { comments: { 7: [override(author)] } }));
    assert.equal(r.status.state, state, `${labeller.login}/${author.login}: ${r.status.description}`);
    assert.equal(r.status.description, description);
  }
});

test('AC2: any one of the owner\'s matching comments counts among others\', and EMERGENCY BYPASS is one', async () => {
  let r = await gate(withLabels([['gate-override', OWNER]], { comments: { 7: [override(AGENT), override(OWNER)] } }));
  assert.equal(r.status.state, 'success');
  r = await gate(withLabels([['gate-override', OWNER]], { comments: { 7: [override(OWNER, 'EMERGENCY BYPASS: production is down')] } }));
  assert.equal(r.status.state, 'success');
  r = await gate(withLabels([['gate-override', OWNER]], { comments: { 7: [override(BOT)] } }));
  assert.equal(r.status.state, 'failure', 'a bot\'s comment never counts');
});

// ------------------------------------------------------------------------------------------------- AC3

test('⛔ AC3: the lane needs the owner\'s uat:skip on the issue; an agent\'s uat:skip on the PR is fine', async () => {
  const world = (actor) => ({
    prs: { 7: { number: 7, title: '#5: a change', head: { ref: '5-a-change', sha: 'f'.repeat(40) }, labels: ['uat:skip'], draft: false, auto_merge: null } },
    events: { 7: [labelled('uat:skip', AGENT)], 5: [labelled('uat:skip', actor)] },
    issues: { 5: { labels: ['uat:skip'] } },
  });
  let r = await gate(world(OWNER));
  assert.equal(r.status.state, 'success', r.status.description);
  assert.match(r.status.description, /No UAT needed/);
  for (const actor of [AGENT, BOT]) {
    r = await gate(world(actor));
    assert.equal(r.status.state, 'failure', actor.login);
    assert.equal(r.status.description, `uat:skip on #5 was added by @${actor.login}, not the owner: needs UAT`);
  }
});

test('AC3: on the issue\'s own labeled event its sender counts', async () => {
  const world = {
    prs: { 7: { number: 7, title: '#5: a change', head: { ref: '5-a-change', sha: 'f'.repeat(40) }, labels: ['uat:skip'], draft: false, auto_merge: null } },
    issues: { 5: { labels: ['uat:skip'] } },
  };
  const r = await gate(world, { eventName: 'issues', payload: { action: 'labeled', label: { name: 'uat:skip' }, issue: { number: 5 }, pull_request: undefined, sender: OWNER } });
  assert.equal(r.status.state, 'success', r.status.description);
});

// ------------------------------------------------------------------------------------------------- AC5

test('⛔ AC5: with no owner in haam.config.json, or no config at all, no owner label or override counts', async () => {
  for (const config of [null, { ...CONFIG, product_owner_github: '' }, { tracker: 'github' }]) {
    let r = await gate(withLabels([['uat-passed', OWNER]], { config }));
    assert.equal(r.status.state, 'failure', JSON.stringify(config));
    assert.equal(r.status.description, 'No owner in haam.config.json on main: owner labels don\'t count');
    r = await gate(withLabels([['gate-override', OWNER]], { config, comments: { 7: [override(OWNER)] } }));
    assert.equal(r.status.state, 'failure', JSON.stringify(config));
  }
});

// ------------------------------------------------------------------------------------------------- AC6

test('⛔ AC6: a PR with auto-merge on loses it when its uat-passed is not the owner\'s', async () => {
  const world = withLabels([['uat-passed', AGENT]]);
  world.prs[7].auto_merge = { enabled_by: AGENT };
  const r = await gate(world);
  assert.equal(r.outputs.disable, '7');
  const ok = withLabels([['uat-passed', OWNER]]);
  ok.prs[7].auto_merge = { enabled_by: OWNER };
  assert.equal((await gate(ok)).outputs.disable, '', 'the owner\'s pass keeps it');
});

// ------------------------------------------------------------------------------------------------- AC7

test('⛔ AC7 (changeover, step 1): the gate listens to pull_request_target and, until step 2, to pull_request too; it never checks out or runs anything of the PR', () => {
  const on = /\non:\n([\s\S]*?)\n\S/.exec(GATES)[1];
  const types = '[opened, reopened, synchronize, labeled, unlabeled, ready_for_review, edited]';
  assert.match(on, new RegExp(`^ {2}pull_request_target:\\n {4}types: ${types.replace(/[[\]]/g, '\\$&')}$`, 'm'));
  assert.match(on, new RegExp(`^ {2}pull_request:\\n {4}types: ${types.replace(/[[\]]/g, '\\$&')}$`, 'm'), 'pull_request too, with the same types, so the PR that brings this file is judged');
  assert.match(on, /^ {2}issue_comment:/m);
  assert.match(on, /^ {2}issues:/m);
  assert.equal((GATES.match(/event_name == 'pull_request'/g) ?? []).length, 2, 'pull_request only beside pull_request_target');
  assert.equal((GATES.match(/event_name == 'pull_request_target'/g) ?? []).length, 2);
  assert.equal((GATES.match(/\(github\.event_name == 'pull_request' \|\| github\.event_name == 'pull_request_target'\)/g) ?? []).length, 2);
  assert.doesNotMatch(GATES, /actions\/checkout/, 'no checkout: nothing of the PR is on disk');
  assert.doesNotMatch(GATES, /uses:\s*\.\//, 'no local action');
  assert.doesNotMatch(GATES, /ref:\s*\$\{\{\s*github\.event\.pull_request\.head\.(ref|sha)/, 'no PR head as a ref');
  assert.match(GATES, /^# .*main's copy/m, 'the header says it');
});

test('AC7: the gate\'s results on a pull_request_target event are those of every case above', async () => {
  const r = await gate(withLabels([['uat-passed', OWNER]]), { eventName: 'pull_request_target' });
  assert.equal(r.status.state, 'success');
  const docs = await gate({ files: { 7: ['docs/notes.md'] } });
  assert.equal(docs.status.description, 'Docs-only change: UAT not required');
});

// ------------------------------------------------------------------------------------------------- AC9

test('AC9: the owner-only block is marked, so a kit merge that drops it fails here', () => {
  assert.equal((GATES.match(/>>> owner-only labels/g) ?? []).length, 1);
  assert.equal((GATES.match(/<<< owner-only labels/g) ?? []).length, 1);
});

// ----------------------------------------------------------------------------------- the changeover

/** gates.yml as the kit shipped it at [rev] (e.g. a tag), or null when this checkout does not have it. */
function gatesAt(rev) {
  const r = spawnSync('git', ['-C', KIT, 'show', `${rev}:template/.github/workflows/gates.yml`], { encoding: 'utf8' });
  return r.status === 0 ? r.stdout : null;
}
/** The events a gates.yml listens to, from its `on:` block. */
const triggers = (text) => [.../\non:\n([\s\S]*?)\n\S/.exec(text)[1].matchAll(/^ {2}([a-z_]+):/gm)].map((m) => m[1]);
/** The template as `haam.py update` writes it once main's copy listens to pull_request_target (the same rule as
 *  haam.py's gates_changeover): the lines between the haam:changeover markers removed, the markers with them. */
const STEP2 = GATES.replace(/^[ \t]*(?:#|\/\/) >>> haam:changeover.*\n[\s\S]*?^[ \t]*(?:#|\/\/) <<< haam:changeover.*\n/gm, '');
/** The kit's gates.yml before the owner-only gate: no pull_request_target. */
const OLD = gatesAt('v1.19.0') ?? GATES.replace(/^ {2}pull_request_target:\n {4}types: .*\n/m, '');

async function postersOn(mainText, prText) {
  let posters = 0;
  if (triggers(prText).includes('pull_request')) {
    const r = await gate(withLabels([['uat-passed', OWNER]], { mainGates: mainText }), { eventName: 'pull_request' }, gateScript(prText));
    if (r.statuses.length) posters += 1;
  }
  if (triggers(mainText).includes('pull_request_target')) {
    const r = await gate(withLabels([['uat-passed', OWNER]], { mainGates: mainText }), { eventName: 'pull_request_target' }, gateScript(mainText));
    if (r.statuses.length) posters += 1;
  }
  return posters;
}

test('⛔ changeover: the PR that brings this gates.yml (step 1) gets exactly one release-gate, from its own copy, while main\'s copy is the old one', async () => {
  assert.ok(!triggers(OLD).includes('pull_request_target'), 'the old copy knows no pull_request_target');
  assert.equal(await postersOn(OLD, GATES), 1, 'one run posts: never none (the PR could not merge), never two');
});

test('⛔ changeover: step 2 (the markers\' lines removed) listens to pull_request_target alone, and its PR is judged by main\'s step 1', async () => {
  assert.ok(!triggers(STEP2).includes('pull_request'), STEP2.slice(0, 2000));
  assert.ok(triggers(STEP2).includes('pull_request_target'));
  assert.doesNotMatch(STEP2, /^[ \t]*(?:#|\/\/) (?:>>>|<<<) haam:changeover|context\.eventName === 'pull_request'/m);
  assert.equal(await postersOn(GATES, STEP2), 1, 'main\'s step 1 decides the step-2 PR');
  assert.equal(await postersOn(STEP2, STEP2), 1, 'afterwards, main\'s copy alone');
  const r = await gate(withLabels([['uat-passed', OWNER]]), { eventName: 'pull_request_target' }, gateScript(STEP2));
  assert.equal(r.status.state, 'success');
});

test('⛔ changeover: step 2 merged straight over an old main gets no gate at all, which is why update writes step 1 first', async () => {
  assert.equal(await postersOn(OLD, STEP2), 0);
});

test('⛔ changeover: once main has step 1, the PR\'s own copy posts nothing; only main\'s copy decides', async () => {
  const prRun = await gate(withLabels([['uat-passed', OWNER]]), { eventName: 'pull_request' });
  assert.deepEqual(prRun.statuses, [], 'the pull_request run, the PR\'s copy, posts nothing once main listens to pull_request_target');
  const mainRun = await gate(withLabels([['uat-passed', OWNER]]), { eventName: 'pull_request_target' });
  assert.equal(mainRun.status.state, 'success');
});

test('⛔ changeover: when main\'s copy cannot be read, the PR\'s own copy posts nothing (main\'s run, if any, decides; never two)', async () => {
  const r = await gate(withLabels([['uat-passed', OWNER]], { mainGates: null }), { eventName: 'pull_request' });
  assert.deepEqual(r.statuses, []);
  assert.ok(r.warnings.some((w) => /main's copy of gates\.yml/.test(w)), r.warnings.join('\n'));
});
