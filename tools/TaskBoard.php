<?php

/**
 * Reads the task files under app/dev/tasks and renders the board.
 *
 * The board is generated rather than maintained because a hand-edited index is
 * the shared file the one-task-per-file rule exists to avoid — everyone would
 * have to touch it to record anything, and the conflicts would land in the
 * lines that say what is done (app/dev/PROCESS.md).
 *
 * The same reader holds the rules the planning documents have to obey, so
 * `bin/tasks --check` and `TaskBoardTest` apply one implementation rather
 * than two hand-kept copies. Each rule is a method returning the violations
 * it found, as sentences a developer can act on; `problems()` is all of them.
 *
 * The front matter is parsed here rather than with a YAML library. It is flat
 * `key: value` by design, symfony/yaml is only present transitively, and
 * fifteen lines with no dependency is the cheaper of the two risks.
 */
class TaskBoard
{
    public const DIRECTORY = 'app/dev/tasks';

    public const REPORTS = 'app/dev/tasks/reports';

    public const STREAMS = 'app/dev/streams';

    public const BOARD = 'app/dev/BOARD.md';

    public const TEMPLATE = 'app/dev/tasks/TEMPLATE.md';

    /** How many `ready` tasks the board aims to keep, so nobody waits for a spec. */
    public const READY_TARGET = 4;

    /** In the order the board shows them: what to do next comes first. */
    public const STATUSES = ['doing', 'ready', 'rescope', 'blocked', 'draft', 'done'];

    /**
     * From this report date on, every "Found, not fixed" bullet ends in a
     * disposition. Older reports are counted as untriaged, not rewritten.
     */
    public const DISPOSITION_CUTOFF = '2026-09-15';

    /** `→ T-###`, `→ draft T-###` or `→ decided: <why not>`, at the end of a finding. */
    public const DISPOSITION = '/→ (T-\d{3}|draft T-\d{3}|decided: \S.*)$/u';

    /** A task whose Files touch one of these rewires a flow, and says which flow file records it. */
    public const FLOW_PATHS = ['app/Http/', 'app/Services/', 'app/Listeners/', 'routes/'];

    /** The status words a stream file may not carry: the board says what is done. */
    public const STATUS_WORDS = '/~~|\*\*(done|ready|draft|doing|blocked|rescope)\b|—\s*(done|ready|draft|doing|blocked|rescope)\s*$/m';

    /** How many days a report stays "recent" for the spec-overlap warning. */
    public const OVERLAP_DAYS = 7;

    /** @var list<array<string, mixed>> */
    private array $tasks;

    /** @var array<string, array<string, mixed>> keyed by stream slug */
    private array $streams;

    /** @var list<array<string, mixed>> */
    private array $reports;

    /**
     * @param  string  $root  Absolute path to the repository root.
     */
    public function __construct(private string $root)
    {
        $this->tasks = $this->read();
        $this->streams = $this->readStreams();
        $this->reports = $this->readReports();
    }

    /** @return list<array<string, mixed>> */
    public function tasks(): array
    {
        return $this->tasks;
    }

    /** @return array<string, array<string, mixed>> */
    public function streams(): array
    {
        return $this->streams;
    }

    /** @return list<array<string, mixed>> */
    public function reports(): array
    {
        return $this->reports;
    }

    /** The id a new task takes: one past the highest file, whatever its status. */
    public function nextId(): string
    {
        $highest = 0;

        foreach ($this->tasks as $task) {
            $highest = max($highest, (int) substr((string) $task['id'], 2));
        }

        return sprintf('T-%03d', $highest + 1);
    }

    /** How many `ready` tasks the plan wants on the board: ready ≥ 2 × active developers. */
    public function readyTarget(): int
    {
        return self::READY_TARGET;
    }

    /**
     * Files claimed by more than one task that is being worked on right now.
     *
     * The point of listing files in a spec: a collision is visible before two
     * developers meet in a merge, rather than after.
     *
     * @return array<string, list<string>>
     */
    public function collisions(): array
    {
        $claims = [];

        foreach ($this->tasks as $task) {
            if ($task['status'] !== 'doing') {
                continue;
            }

            foreach ($task['files'] as $file) {
                $claims[$file][] = $task['id'];
            }
        }

        return array_filter($claims, fn (array $ids): bool => count($ids) > 1);
    }

    /**
     * Tasks under way whose dependencies are not finished.
     *
     * @return list<string>
     */
    public function brokenDependencies(): array
    {
        $done = [];

        foreach ($this->tasks as $task) {
            if ($task['status'] === 'done') {
                $done[] = $task['id'];
            }
        }

        $broken = [];

        foreach ($this->tasks as $task) {
            if (! in_array($task['status'], ['doing', 'done'], true)) {
                continue;
            }

            foreach ($task['depends'] as $dependency) {
                if (! in_array($dependency, $done, true)) {
                    $broken[] = "{$task['id']} ({$task['status']}) depends on {$dependency}, which is not done";
                }
            }
        }

        return $broken;
    }

    /**
     * Task id => the ids that depend on it, derived from `depends:`.
     *
     * `blocks:` stays in the front matter for a reader, but it is the inverse
     * of `depends:` and a hand-kept inverse drifts — it was wrong in ten places
     * when this was written. The derived value is the truth; the field has to
     * agree with it (see blocksDisagreements()).
     *
     * @return array<string, list<string>>
     */
    public function blockedBy(): array
    {
        $blocked = [];

        foreach ($this->tasks as $task) {
            foreach ($task['depends'] as $dependency) {
                $blocked[$dependency][] = $task['id'];
            }
        }

        foreach ($blocked as &$ids) {
            sort($ids);
        }

        ksort($blocked);

        return $blocked;
    }

    /**
     * Ready tasks sharing a file with a task somebody reported on recently.
     *
     * A spec written against a file that changed last week may name a method
     * that no longer exists. Not a failure — the developer who claims the task
     * reads the report first, which is what reports are for.
     *
     * @return list<array{id: string, file: string, with: string}>
     */
    public function overlaps(): array
    {
        $since = date('Y-m-d', strtotime('-'.self::OVERLAP_DAYS.' days'));
        $recent = [];

        foreach ($this->reports as $report) {
            if ($report['date'] >= $since) {
                $recent[$report['task']] = true;
            }
        }

        $byId = array_column($this->tasks, null, 'id');
        $overlaps = [];

        foreach ($this->tasks as $task) {
            if ($task['status'] !== 'ready') {
                continue;
            }

            foreach (array_keys($recent) as $reported) {
                if ($reported === $task['id'] || ! isset($byId[$reported])) {
                    continue;
                }

                foreach (array_intersect($task['files'], $byId[$reported]['files']) as $file) {
                    $overlaps[] = ['id' => $task['id'], 'file' => $file, 'with' => $reported];
                }
            }
        }

        return $overlaps;
    }

    /** Report findings under "Found, not fixed" that end in no disposition, across every report. */
    public function untriaged(): int
    {
        $count = 0;

        foreach ($this->reports as $report) {
            $count += count($report['untriaged']);
        }

        return $count;
    }

    /**
     * Every rule, as the sentences a developer can act on. Empty is green.
     *
     * @return list<string>
     */
    public function problems(): array
    {
        $problems = [];

        foreach ($this->collisions() as $file => $ids) {
            $problems[] = sprintf('Collision: %s is claimed by %s, both in progress.', $file, implode(' and ', $ids));
        }

        foreach ($this->brokenDependencies() as $warning) {
            $problems[] = 'Out of order: '.$warning.'.';
        }

        return [
            ...$problems,
            ...$this->bareBasenames(),
            ...$this->blocksDisagreements(),
            ...$this->blockedWithoutReason(),
            ...$this->largeWithoutSplit(),
            ...$this->rewiresWithoutFlow(),
            ...$this->streamsWithStatusWords(),
            ...$this->streamsNamingMissingTasks(),
            ...$this->streamsNotIndexed(),
            ...$this->undisposedFindings(),
        ];
    }

    /**
     * A Files row that is a bare basename claims nothing the collision check
     * can compare: `SeriesService.php` and `app/Services/SeriesService.php`
     * never match. A path with no directory is allowed only for a file at the
     * repository root, or one the row marks `new`.
     *
     * @return list<string>
     */
    public function bareBasenames(): array
    {
        $problems = [];

        foreach ($this->tasks as $task) {
            if (! in_array($task['status'], ['ready', 'doing'], true)) {
                continue;
            }

            foreach ($task['files'] as $file) {
                if (str_contains($file, '/') || in_array($file, $task['new'], true) || file_exists($this->root.'/'.$file)) {
                    continue;
                }

                $problems[] = "{$task['id']} lists `{$file}` with no directory, and no such file is at the repository root.";
            }
        }

        return $problems;
    }

    /** @return list<string> */
    public function blocksDisagreements(): array
    {
        $derived = $this->blockedBy();
        $problems = [];

        foreach ($this->tasks as $task) {
            $stated = $task['blocks'];
            sort($stated);
            $expected = $derived[$task['id']] ?? [];

            if ($stated !== $expected) {
                $problems[] = sprintf(
                    '%s says blocks: %s, but depends: across the tasks derives %s.',
                    $task['id'],
                    $stated === [] ? 'none' : implode(', ', $stated),
                    $expected === [] ? 'none' : implode(', ', $expected),
                );
            }
        }

        return $problems;
    }

    /**
     * A blocked task says what it waits on and who can unblock it, under
     * `## Blocked on`, as a `What:` line and a `Who:` line.
     *
     * @return list<string>
     */
    public function blockedWithoutReason(): array
    {
        $problems = [];

        foreach ($this->tasks as $task) {
            if ($task['status'] !== 'blocked') {
                continue;
            }

            $section = $this->section($task['contents'], 'Blocked on');

            if ($section === null) {
                $problems[] = "{$task['id']} is blocked with no `## Blocked on` section.";

                continue;
            }

            foreach (['What:', 'Who:'] as $label) {
                if (! preg_match('/^\**'.preg_quote($label, '/').'\**\s*\S/m', $section)) {
                    $problems[] = "{$task['id']} is blocked and its `## Blocked on` has no `{$label}` line.";
                }
            }
        }

        return $problems;
    }

    /**
     * An `L` estimate usually means two tasks. A ready one either names in
     * `blocks:` the tasks it was cut to precede, or carries a `Split:` line
     * saying why it stays whole.
     *
     * @return list<string>
     */
    public function largeWithoutSplit(): array
    {
        $problems = [];

        foreach ($this->tasks as $task) {
            if ($task['status'] !== 'ready' || $task['estimate'] !== 'L') {
                continue;
            }

            if ($task['blocks'] !== [] || preg_match('/^\**Split:\**\s*\S/m', $task['contents'])) {
                continue;
            }

            $problems[] = "{$task['id']} is a ready L task with nothing in blocks: and no `Split:` line.";
        }

        return $problems;
    }

    /**
     * A task that edits a controller, service, listener or route file changes
     * a call chain, and docs/flows/ is the record of call chains. The task
     * names the flow file it will update, or says `Flows: none — <reason>`.
     *
     * @return list<string>
     */
    public function rewiresWithoutFlow(): array
    {
        $problems = [];

        foreach ($this->tasks as $task) {
            if (! in_array($task['status'], ['ready', 'doing'], true)) {
                continue;
            }

            $rewires = false;

            foreach ($task['files'] as $file) {
                foreach (self::FLOW_PATHS as $prefix) {
                    if (str_starts_with($file, $prefix)) {
                        $rewires = true;
                    }
                }
            }

            if (! $rewires) {
                continue;
            }

            if (preg_match('#docs/flows/[\w-]+\.md#', $task['contents']) || preg_match('/^\**Flows: none\**\s*—\s*\S/m', $task['contents'])) {
                continue;
            }

            $problems[] = "{$task['id']} edits a controller, service, listener or route file and names no docs/flows/*.md, nor a `Flows: none — <reason>` line.";
        }

        return $problems;
    }

    /**
     * Status lives in task files only. A stream file that says "done" or
     * strikes a line through is a second copy of the board, kept by hand.
     *
     * @return list<string>
     */
    public function streamsWithStatusWords(): array
    {
        $problems = [];

        foreach ($this->streams as $slug => $stream) {
            $body = substr($stream['contents'], $stream['bodyOffset']);

            if (preg_match_all(self::STATUS_WORDS, $body, $matches, PREG_OFFSET_CAPTURE) === 0) {
                continue;
            }

            foreach ($matches[0] as [$word, $offset]) {
                $line = substr_count(substr($body, 0, $offset), "\n") + 1 + $stream['bodyLine'];
                $problems[] = "Stream {$slug} carries a status word or strikethrough at line {$line}: `".trim($word).'`.';
            }
        }

        return array_values(array_unique($problems));
    }

    /**
     * Every `T-###` a stream mentions exists, and every task in its ordered
     * list belongs to it.
     *
     * @return list<string>
     */
    public function streamsNamingMissingTasks(): array
    {
        $byId = array_column($this->tasks, null, 'id');
        $problems = [];

        foreach ($this->streams as $slug => $stream) {
            foreach ($stream['names'] as $id) {
                if (! isset($byId[$id])) {
                    $problems[] = "Stream {$slug} names {$id}, which does not exist.";
                }
            }

            foreach ($stream['ordered'] as $id) {
                if (isset($byId[$id]) && $byId[$id]['stream'] !== $slug) {
                    $problems[] = "Stream {$slug} lists {$id} in its tasks, but {$id} belongs to {$byId[$id]['stream']}.";
                }
            }
        }

        return $problems;
    }

    /** @return list<string> */
    public function streamsNotIndexed(): array
    {
        $index = $this->root.'/'.self::STREAMS.'/README.md';
        $contents = file_exists($index) ? (string) file_get_contents($index) : '';
        $problems = [];

        foreach (array_keys($this->streams) as $slug) {
            if (! str_contains($contents, '('.$slug.'.md)')) {
                $problems[] = "Stream {$slug} is not listed in streams/README.md.";
            }
        }

        return $problems;
    }

    /**
     * From the cutoff, a report's "Found, not fixed" bullets each end in a
     * disposition: `→ T-###`, `→ draft T-###` or `→ decided: <why not>`.
     *
     * @return list<string>
     */
    public function undisposedFindings(): array
    {
        $problems = [];

        foreach ($this->reports as $report) {
            if ($report['date'] < self::DISPOSITION_CUTOFF) {
                continue;
            }

            foreach ($report['untriaged'] as $finding) {
                $problems[] = sprintf('%s has a finding with no disposition: "%s…"', $report['file'], mb_substr($finding, 0, 60));
            }
        }

        return $problems;
    }

    public function render(): string
    {
        $lines = [
            '# Task board',
            '',
            '> Generated by `bin/tasks`. **Do not edit.** Change a task file',
            '> and regenerate — see [`PROCESS.md`](PROCESS.md).',
            '',
            '[Current plan](../PLAN.md) | [Process](PROCESS.md) | [Streams](streams/)',
            '',
        ];

        $lines = [...$lines, ...$this->renderSummary(), ...$this->renderWarnings()];
        $blockedBy = $this->blockedBy();

        foreach ($this->byStream() as $stream => $tasks) {
            $lines[] = '## '.$stream;
            $lines[] = '';

            // Nobody owns a stream (D-043). Whoever has a task in it in
            // progress is on it, and that is all the board needs to say.
            $onIt = [];

            foreach ($tasks as $task) {
                if ($task['status'] === 'doing') {
                    $onIt[$task['owner']][] = $task['id'];
                }
            }

            if ($onIt !== []) {
                $lines[] = 'On it: '.implode('; ', array_map(
                    fn (string $who, array $ids): string => $who.' ('.implode(', ', $ids).')',
                    array_keys($onIt),
                    $onIt,
                ));
                $lines[] = '';
            }

            $lines[] = '| Task | Title | Status | Owner | Est | Depends | Blocks |';
            $lines[] = '| ---- | ----- | ------ | ----- | --- | ------- | ------ |';

            foreach ($tasks as $task) {
                $depends = $task['depends'] === [] ? '—' : implode(', ', $task['depends']);
                $blocks = ($blockedBy[$task['id']] ?? []) === [] ? '—' : implode(', ', $blockedBy[$task['id']]);
                $owner = $task['owner'] === 'unassigned' ? '—' : $task['owner'];

                $lines[] = sprintf(
                    '| [%s](tasks/%s) | %s | %s | %s | %s | %s | %s |',
                    $task['id'],
                    $task['file'],
                    $task['title'],
                    $this->badge($task['status']),
                    $owner,
                    $task['estimate'],
                    $depends,
                    $blocks,
                );
            }

            $lines[] = '';
        }

        return implode("\n", $lines)."\n";
    }

    /** @return list<string> */
    private function renderSummary(): array
    {
        $counts = array_fill_keys(self::STATUSES, 0);

        foreach ($this->tasks as $task) {
            if (isset($counts[$task['status']])) {
                $counts[$task['status']]++;
            }
        }

        $cells = [];

        foreach ($counts as $status => $count) {
            $cells[] = $this->badge($status).' '.$count;
        }

        return [implode(' · ', $cells), ''];
    }

    /** @return list<string> */
    private function renderWarnings(): array
    {
        $problems = $this->problems();
        $overlaps = $this->overlaps();

        if ($problems === [] && $overlaps === []) {
            return [];
        }

        $lines = ['## Needs attention', ''];

        foreach ($problems as $problem) {
            $lines[] = '- '.$problem;
        }

        $grouped = [];

        foreach ($overlaps as $overlap) {
            $grouped[$overlap['id']][$overlap['file']][] = $overlap['with'];
        }

        foreach ($grouped as $id => $files) {
            foreach ($files as $file => $reported) {
                $lines[] = "- **Spec overlap** — {$id} is ready and names `{$file}`, reported on in the last ".self::OVERLAP_DAYS.' days by '.implode(', ', $reported).'.';
            }
        }

        $lines[] = '';

        return $lines;
    }

    private function badge(string $status): string
    {
        return match ($status) {
            'doing' => '🔨 doing',
            'ready' => '🟢 ready',
            'rescope' => '🔁 rescope',
            'blocked' => '⛔ blocked',
            'done' => '✅ done',
            default => '📝 draft',
        };
    }

    /** @return array<string, list<array<string, mixed>>> */
    private function byStream(): array
    {
        $streams = [];

        foreach ($this->tasks as $task) {
            $streams[$task['stream']][] = $task;
        }

        ksort($streams);

        return $streams;
    }

    /** @return list<array<string, mixed>> */
    private function read(): array
    {
        $paths = glob($this->root.'/'.self::DIRECTORY.'/T-*.md') ?: [];
        sort($paths);

        $tasks = [];

        foreach ($paths as $path) {
            $contents = (string) file_get_contents($path);
            $front = $this->frontMatter($contents);

            if ($front === []) {
                continue;
            }

            $order = array_search($front['status'] ?? 'draft', self::STATUSES, true);
            [$files, $new] = $this->files($contents);

            $tasks[] = [
                'id' => $front['id'] ?? basename($path, '.md'),
                'file' => basename($path),
                'title' => $front['title'] ?? '',
                'stream' => $front['stream'] ?? 'unassigned',
                'status' => $front['status'] ?? 'draft',
                'owner' => $front['owner'] ?? 'unassigned',
                'estimate' => $front['estimate'] ?? '?',
                'depends' => $this->list($front['depends'] ?? 'none'),
                'blocks' => $this->list($front['blocks'] ?? 'none'),
                'files' => $files,
                'new' => $new,
                'contents' => $contents,
                'order' => $order === false ? count(self::STATUSES) : $order,
            ];
        }

        usort($tasks, fn (array $a, array $b): int => [$a['order'], $a['id']] <=> [$b['order'], $b['id']]);

        return $tasks;
    }

    /**
     * Every stream file but the index, with the tasks it names.
     *
     * @return array<string, array<string, mixed>>
     */
    private function readStreams(): array
    {
        $paths = glob($this->root.'/'.self::STREAMS.'/*.md') ?: [];
        sort($paths);

        $streams = [];

        foreach ($paths as $path) {
            if (basename($path) === 'README.md') {
                continue;
            }

            $contents = (string) file_get_contents($path);
            $bodyOffset = $this->bodyOffset($contents);

            preg_match_all('/\bT-\d{3}\b/', $contents, $names);

            $ordered = [];
            $list = $this->section($contents, 'Tasks, in order') ?? '';

            if (preg_match_all('/^\s*(?:\d+\.|-)\s+.*?(T-\d{3})/m', $list, $items)) {
                $ordered = $items[1];
            }

            $streams[basename($path, '.md')] = [
                'file' => basename($path),
                'contents' => $contents,
                'bodyOffset' => $bodyOffset,
                'bodyLine' => substr_count(substr($contents, 0, $bodyOffset), "\n"),
                'names' => array_values(array_unique($names[0])),
                'ordered' => array_values(array_unique($ordered)),
            ];
        }

        return $streams;
    }

    /**
     * Every report, with its date and the findings that end in no disposition.
     *
     * @return list<array<string, mixed>>
     */
    private function readReports(): array
    {
        $paths = glob($this->root.'/'.self::REPORTS.'/T-*.md') ?: [];
        sort($paths);

        $reports = [];

        foreach ($paths as $path) {
            $contents = (string) file_get_contents($path);
            $front = $this->frontMatter($contents);
            $date = $front['date'] ?? null;

            if (! is_string($date) || ! preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
                $date = preg_match('/^T-\d{3}-(\d{4}-\d{2}-\d{2})/', basename($path), $m) ? $m[1] : '0000-00-00';
            }

            $findings = $this->findings($this->section($contents, 'Found, not fixed') ?? '');

            $reports[] = [
                'file' => basename($path),
                'task' => substr(basename($path), 0, 5),
                'date' => $date,
                'findings' => $findings,
                'untriaged' => array_values(array_filter($findings, fn (string $finding): bool => preg_match(self::DISPOSITION, $finding) !== 1)),
            ];
        }

        return $reports;
    }

    /**
     * The findings in a "Found, not fixed" section: each top-level bullet, or
     * each paragraph where the section is written as prose. Continuation lines
     * join their item so the disposition can sit on the last line.
     *
     * @return list<string>
     */
    private function findings(string $section): array
    {
        $items = [];
        $current = null;

        foreach (explode("\n", $section) as $line) {
            if (trim($line) === '') {
                if ($current !== null) {
                    $items[] = $current;
                }
                $current = null;

                continue;
            }

            if (preg_match('/^(?:[-*]|\d+\.)\s+(.*)$/', $line, $m)) {
                if ($current !== null) {
                    $items[] = $current;
                }
                $current = $m[1];

                continue;
            }

            $current = $current === null ? trim($line) : $current.' '.trim($line);
        }

        if ($current !== null) {
            $items[] = $current;
        }

        return array_values(array_filter(
            array_map(fn (string $item): string => trim($item), $items),
            fn (string $item): bool => ! in_array(strtolower(trim($item, '*_ .')), ['none', 'nothing'], true),
        ));
    }

    /** The body of one `## Heading`, up to the next `## `, or null when the heading is absent. */
    private function section(string $contents, string $heading): ?string
    {
        $start = strpos($contents, "\n## ".$heading);

        if ($start === false) {
            return null;
        }

        $start += strlen("\n## ".$heading);
        $end = strpos($contents, "\n## ", $start);

        $section = substr($contents, $start, $end === false ? null : $end - $start);

        return substr($section, (int) strpos($section, "\n"));
    }

    /** @return array<string, string> */
    private function frontMatter(string $contents): array
    {
        if (! str_starts_with($contents, "---\n")) {
            return [];
        }

        $end = strpos($contents, "\n---", 4);

        if ($end === false) {
            return [];
        }

        $front = [];

        foreach (explode("\n", substr($contents, 4, $end - 4)) as $line) {
            if (! str_contains($line, ':')) {
                continue;
            }

            [$key, $value] = explode(':', $line, 2);
            $front[trim($key)] = trim($value);
        }

        return $front;
    }

    /** Where the front matter ends and the document starts. */
    private function bodyOffset(string $contents): int
    {
        if (! str_starts_with($contents, "---\n")) {
            return 0;
        }

        $end = strpos($contents, "\n---", 4);

        return $end === false ? 0 : $end + strlen("\n---");
    }

    /** @return list<string> */
    private function list(string $value): array
    {
        if ($value === '' || mb_strtolower($value) === 'none') {
            return [];
        }

        return array_values(array_filter(array_map('trim', explode(',', $value))));
    }

    /**
     * The paths a task claims: every backticked path in the first cell of
     * every row of its Files table, with globs expanded against the repository.
     *
     * A glob that matches nothing stays as written, so two tasks naming the
     * same pattern for files that do not exist yet still collide.
     *
     * @return array{0: list<string>, 1: list<string>} the paths, and the subset marked `new`
     */
    private function files(string $contents): array
    {
        $section = $this->section($contents, 'Files');

        if ($section === null) {
            return [[], []];
        }

        $files = [];
        $new = [];

        foreach (explode("\n", $section) as $line) {
            if (! preg_match('/^\|([^|]*)\|([^|]*)\|/', $line, $cells)) {
                continue;
            }

            preg_match_all('/`([^`]+)`/', $cells[1], $paths);
            $isNew = trim($cells[2]) === 'new';

            foreach ($paths[1] as $path) {
                foreach ($this->expand($path) as $expanded) {
                    $files[] = $expanded;

                    if ($isNew) {
                        $new[] = $expanded;
                    }
                }
            }
        }

        return [array_values(array_unique($files)), array_values(array_unique($new))];
    }

    /** @return list<string> */
    private function expand(string $path): array
    {
        if (! preg_match('/[*?\[{]/', $path)) {
            return [$path];
        }

        $matches = glob($this->root.'/'.$path, GLOB_BRACE) ?: [];

        if ($matches === []) {
            return [$path];
        }

        return array_map(fn (string $match): string => substr($match, strlen($this->root) + 1), $matches);
    }
}
