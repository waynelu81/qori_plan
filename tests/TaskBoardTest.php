<?php

use PHPUnit\Framework\TestCase;

/**
 * The planning board, and the rules that keep the task files usable.
 *
 * Most of these assert against the real `app/dev/tasks` directory rather
 * than a fixture, on purpose: the point is not that the parser works, it is
 * that the plan itself stays consistent. The fixture under
 * tests/Fixtures/planning is for the parser and the renderer — the rendered
 * board is not committed and there is nothing live to compare it with, and a
 * rule is only known to catch anything if it is shown catching something. A
 * task that depends on an id nobody created, or two people holding the same
 * file, should fail the gate — that is cheaper than either being discovered
 * in a merge.
 *
 * The rules themselves live in TaskBoard, so `qori:tasks --check` and this
 * suite apply one implementation. Each test here asserts one rule holds on the
 * live directory; the fixture shows the rule firing.
 *
 * @see app/dev/PROCESS.md
 */
class TaskBoardTest extends TestCase
{
    private static function root(): string
    {
        return dirname(__DIR__);
    }

    private function board(): TaskBoard
    {
        return new TaskBoard(self::root());
    }

    private function fixture(): TaskBoard
    {
        return new TaskBoard(self::root().'/tests/Fixtures/planning');
    }

    /** @return list<string> */
    private function taskFiles(): array
    {
        return glob(self::root().'/'.TaskBoard::DIRECTORY.'/T-*.md') ?: [];
    }

    /** @return array<string, mixed> */
    private function fixtureTask(string $id): array
    {
        foreach ($this->fixture()->tasks() as $task) {
            if ($task['id'] === $id) {
                return $task;
            }
        }

        $this->fail("No fixture task {$id}.");
    }

    /**
     * The board renders, from a fixture rather than the live directory.
     *
     * It used to assert the committed BOARD.md matched a fresh render. The
     * board is no longer committed: every claim or close rewrote its count
     * line and re-sorted its tables, so two people finishing on one day
     * conflicted in a file neither had edited, and the freshness check turned
     * every merge into a red gate. The derivation is what is worth keeping,
     * so this asserts the renderer over two known tasks — including the
     * Blocks column, which is derived from `depends:` rather than read.
     */
    public function test_the_board_renders_from_the_task_files(): void
    {
        $rendered = $this->fixture()->render();

        $this->assertStringContainsString('🔨 doing 1 · 🟢 ready 0 · 🔁 rescope 0 · ⛔ blocked 0 · 📝 draft 0 · ✅ done 1', $rendered);
        $this->assertStringContainsString('## fixture', $rendered);
        $this->assertStringContainsString('| [T-001](tasks/T-001-first.md) | The first fixture task | ✅ done | someone | S | — | T-002 |', $rendered);
        $this->assertStringContainsString('| [T-002](tasks/T-002-second.md) | The second fixture task | 🔨 doing | someone | M | T-001 | — |', $rendered);
    }

    public function test_every_task_file_parses(): void
    {
        $this->assertCount(count($this->taskFiles()), $this->board()->tasks());
    }

    /** An id that does not match its filename breaks every link on the board. */
    public function test_every_id_matches_its_filename(): void
    {
        foreach ($this->board()->tasks() as $task) {
            $this->assertStringStartsWith($task['id'].'-', $task['file']);
        }
    }

    public function test_every_id_is_unique(): void
    {
        $ids = array_column($this->board()->tasks(), 'id');

        $this->assertSame(array_unique($ids), $ids);
    }

    public function test_every_status_is_one_the_process_defines(): void
    {
        foreach ($this->board()->tasks() as $task) {
            $this->assertContains($task['status'], TaskBoard::STATUSES, "{$task['id']} has an unknown status.");
        }
    }

    /** A dependency on an id nobody created is a plan that cannot be followed. */
    public function test_every_dependency_names_a_real_task(): void
    {
        $tasks = $this->board()->tasks();
        $ids = array_column($tasks, 'id');

        foreach ($tasks as $task) {
            foreach ([...$task['depends'], ...$task['blocks']] as $reference) {
                $this->assertContains($reference, $ids, "{$task['id']} references {$reference}, which does not exist.");
            }
        }
    }

    /** Every task belongs to a stream, and every stream is written down. */
    public function test_every_stream_has_a_file(): void
    {
        foreach ($this->board()->tasks() as $task) {
            $this->assertFileExists(
                self::root()."/".TaskBoard::STREAMS."/{$task['stream']}.md",
                "{$task['id']} is in stream '{$task['stream']}', which has no stream file.",
            );
        }
    }

    /**
     * A `ready` task is one somebody can pick up without asking a question, so
     * it has to carry the sections that answer them.
     *
     * Ready and doing only: the list grows as the template does, and a task
     * finished before a section existed is history, not a defect.
     */
    public function test_a_ready_task_carries_every_required_section(): void
    {
        $required = [
            '## Why',
            '## Decisions taken to make this specifiable',
            '## Preconditions',
            '## Scope',
            '## Files',
            '## Database',
            '## Code',
            '## Copy',
            '## Routes',
            '## Tests',
            '## Acceptance',
        ];

        foreach ($this->board()->tasks() as $task) {
            if (! in_array($task['status'], ['ready', 'doing'], true)) {
                continue;
            }

            foreach ($required as $heading) {
                $this->assertStringContainsString($heading, $task['contents'], "{$task['id']} is {$task['status']} and has no {$heading} section.");
            }
        }
    }

    /** And it names the files it will touch, which is what makes parallel work safe. */
    public function test_a_ready_task_claims_at_least_one_file(): void
    {
        // Vacuous when nothing is ready or in progress, which happens whenever
        // the board is caught up. Asserted so a green run means "checked".
        $this->assertNotEmpty($this->board()->tasks());

        foreach ($this->board()->tasks() as $task) {
            if (! in_array($task['status'], ['ready', 'doing'], true)) {
                continue;
            }

            $this->assertNotEmpty($task['files'], "{$task['id']} is {$task['status']} and claims no files.");
        }
    }

    /**
     * A Files row may carry more than one path, and the collision check has to
     * see all of them — the rows most likely to collide are the ones that say
     * "these three files".
     */
    public function test_every_backticked_path_in_a_files_row_is_captured(): void
    {
        $files = $this->fixtureTask('T-002')['files'];

        $this->assertContains('app/Two.php', $files);
        $this->assertContains('app/Three.php', $files);
    }

    /**
     * A glob is a claim on every file it matches today, and the collision check
     * compares paths — so it is expanded here rather than compared as a string
     * that matches nothing. One that matches nothing yet stays as written, so
     * two tasks naming the same pattern still meet.
     */
    public function test_a_glob_in_a_files_row_expands_against_the_repo(): void
    {
        $files = $this->fixtureTask('T-002')['files'];

        $this->assertContains('app/dev/tasks/T-001-first.md', $files);
        $this->assertContains('app/dev/tasks/T-002-second.md', $files);
        $this->assertNotContains('app/dev/tasks/T-00*.md', $files);
        $this->assertContains('app/New/*.php', $files);
    }

    /**
     * `SeriesService.php` and `app/Services/SeriesService.php` never collide,
     * so a bare basename is a claim the board cannot check. Root files and
     * files the row marks `new` are the two honest exceptions.
     */
    public function test_a_files_row_may_not_be_a_bare_basename(): void
    {
        $this->assertSame(
            ['T-002 lists `Bare.php` with no directory, and no such file is at the repository root.'],
            $this->fixture()->bareBasenames(),
        );

        $this->assertSame([], $this->board()->bareBasenames());
    }

    /** Two people editing one file is a merge nobody planned. */
    public function test_no_two_tasks_in_progress_claim_the_same_file(): void
    {
        $this->assertSame([], $this->board()->collisions());
    }

    /** Work started before what it depends on is work that will be redone. */
    public function test_nothing_started_ahead_of_its_dependencies(): void
    {
        $this->assertSame([], $this->board()->brokenDependencies());
    }

    /**
     * `blocks:` is the inverse of `depends:`, kept by hand for a reader. The
     * renderer derives the real value; the field has to agree with it, or the
     * reader is told something the plan does not say.
     */
    public function test_blocks_agrees_with_depends(): void
    {
        $this->assertSame(['T-001' => ['T-002']], $this->fixture()->blockedBy());
        $this->assertSame([], $this->fixture()->blocksDisagreements());

        $this->assertSame([], $this->board()->blocksDisagreements());
    }

    /**
     * The stream owner rewrites a rescoped spec, clears `blocked` and
     * arbitrates a file clash. A stream with nobody named has nobody to ask.
     */
    public function test_every_stream_has_an_owner(): void
    {
        $this->assertNotEmpty($this->board()->streams());
        $this->assertSame('someone', $this->fixture()->streams()['fixture']['owner']);

        $this->assertSame([], $this->board()->streamsWithoutOwner());
    }

    /**
     * Status lives in task files only. A stream that says "done" or strikes a
     * line through is a second copy of the board, and it is the copy that
     * conflicts when two people close tasks in one stream on one afternoon.
     */
    public function test_a_stream_file_carries_no_status_words(): void
    {
        $this->assertMatchesRegularExpression(TaskBoard::STATUS_WORDS, "1. ~~`T-001` — done~~\n");
        $this->assertMatchesRegularExpression(TaskBoard::STATUS_WORDS, "2. `T-002` — **ready**, small\n");
        $this->assertMatchesRegularExpression(TaskBoard::STATUS_WORDS, "3. `T-003` — the last one — done\n");
        $this->assertDoesNotMatchRegularExpression(TaskBoard::STATUS_WORDS, "**Done when.** Every message arrives.\n");

        $this->assertSame([], $this->board()->streamsWithStatusWords());
    }

    /**
     * A stream that names a task nobody created, or lists another stream's
     * task as its own, is a plan two people will read differently.
     */
    public function test_every_task_a_stream_names_exists_and_belongs_to_it(): void
    {
        $this->assertSame(['T-001', 'T-002'], $this->fixture()->streams()['fixture']['ordered']);

        $this->assertSame([], $this->board()->streamsNamingMissingTasks());
    }

    /**
     * `blocked` means "waiting on something outside the repo". A task that
     * does not say what, and who can supply it, waits forever.
     */
    public function test_a_blocked_task_says_what_and_whom_it_waits_on(): void
    {
        // Vacuous when nothing is blocked. Asserted so a green run means "checked".
        $this->assertNotEmpty($this->board()->tasks());

        $this->assertSame([], $this->board()->blockedWithoutReason());
    }

    /**
     * An `L` estimate usually means two tasks (PROCESS.md). One that is ready
     * anyway either names in `blocks:` what it was cut to precede, or says in
     * a `Split:` line why it stays whole.
     */
    public function test_a_ready_l_task_names_its_split(): void
    {
        $this->assertNotEmpty($this->board()->tasks());

        $this->assertSame([], $this->board()->largeWithoutSplit());
    }

    /**
     * From the cutoff, every "Found, not fixed" bullet ends in a disposition —
     * a task, a draft, or a recorded decision not to. Before it, the backlog
     * is counted as untriaged rather than rewritten.
     */
    public function test_a_report_from_the_cutoff_disposes_of_every_finding(): void
    {
        $fixture = $this->fixture();
        $report = $fixture->reports()[0];

        $this->assertSame('2026-09-15', $report['date']);
        $this->assertCount(4, $report['findings']);
        $this->assertSame(['A finding nobody has triaged'], $report['untriaged']);
        $this->assertSame(1, $fixture->untriaged());
        $this->assertCount(1, $fixture->undisposedFindings());
        $this->assertStringContainsString('T-001-2026-09-15-someone.md', $fixture->undisposedFindings()[0]);

        $this->assertSame([], $this->board()->undisposedFindings());
    }

    /**
     * docs/flows/ records call chains. A task that edits a controller, service,
     * listener or route file changes one, and names the flow file it will keep
     * true — or says why there is none.
     */
    public function test_a_task_that_rewires_a_flow_names_its_flow_file(): void
    {
        $this->assertNotEmpty($this->board()->tasks());

        $this->assertSame([], $this->board()->rewiresWithoutFlow());
    }

    /** A stream nobody can find from the index is a stream nobody claims. */
    public function test_every_stream_is_listed_in_the_streams_index(): void
    {
        $this->assertSame([], $this->board()->streamsNotIndexed());
    }

    /** A spec written against a file that changed last week is read beside the report first. */
    public function test_a_spec_overlap_names_the_task_the_file_and_the_report(): void
    {
        foreach ($this->board()->overlaps() as $overlap) {
            $this->assertSame(['id', 'file', 'with'], array_keys($overlap));
            $this->assertNotSame($overlap['id'], $overlap['with']);
        }
    }

    /** The next id is one past the highest file, so two people never pick the same one. */
    public function test_the_next_id_is_one_past_the_highest_file(): void
    {
        $this->assertSame('T-003', $this->fixture()->nextId());
    }

    /** A draft nobody may start still says why it is not ready. */
    public function test_every_draft_says_what_it_is_waiting_on(): void
    {
        foreach ($this->board()->tasks() as $task) {
            if ($task['status'] !== 'draft') {
                continue;
            }

            $this->assertStringContainsString(
                '## Before this can be ready',
                $task['contents'],
                "{$task['id']} is a draft with no note of what it is waiting on.",
            );
        }
    }

    /**
     * A stopped task keeps its evidence.
     *
     * `rescope` is the signal that a specification was wrong, and the log is
     * the whole of what planning has to work from. A status set without one is
     * a task nobody can rewrite.
     */
    public function test_every_rescoped_task_says_what_it_found(): void
    {
        // Vacuous when nothing is rescoped, which is the usual state. Asserted
        // so a green run means "checked", not "found nothing to check".
        $this->assertNotEmpty($this->board()->tasks());

        foreach ($this->board()->tasks() as $task) {
            if ($task['status'] !== 'rescope') {
                continue;
            }

            $log = substr($task['contents'], (int) strpos($task['contents'], '## Re-scope log'));

            $this->assertStringNotContainsString(
                "## Re-scope log\n\nNone.",
                $log,
                "{$task['id']} is rescoped with an empty Re-scope log.",
            );
        }
    }

    /**
     * Finishing includes saying what happened.
     *
     * Four people ran the same four tasks and each found a different subset of
     * the same specification defects. None of it would have reached the person
     * who wrote the specs without this.
     */
    public function test_every_finished_task_has_a_report(): void
    {
        $this->assertDirectoryExists(self::root().'/'.TaskBoard::REPORTS);

        $reported = array_column($this->board()->reports(), 'task');

        foreach ($this->board()->tasks() as $task) {
            if ($task['status'] !== 'done') {
                continue;
            }

            $this->assertContains(
                $task['id'],
                $reported,
                "{$task['id']} is done with no report in tasks/reports/ — see its README.",
            );
        }
    }

    /** A report names a task that exists, or it is filed against nothing. */
    public function test_every_report_names_a_real_task(): void
    {
        $ids = array_column($this->board()->tasks(), 'id');

        $this->assertNotEmpty($ids);

        foreach ($this->board()->reports() as $report) {
            $this->assertContains(
                $report['task'],
                $ids,
                $report['file'].' is a report for a task that does not exist.',
            );
        }
    }

    /** The template is not a task, and must never appear on the board. */
    public function test_the_template_is_not_counted(): void
    {
        $this->assertFileExists(self::root().'/'.TaskBoard::TEMPLATE);
        $this->assertNotContains('T-000', array_column($this->board()->tasks(), 'id'));
    }
}
