"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

import { RuleBadge } from "@/components/event-badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api, EventFilters } from "@/lib/api";

const PAGE_SIZE = 25;

export default function EventsPage() {
  const [rule, setRule] = useState("");
  const [personId, setPersonId] = useState("");
  const [page, setPage] = useState(0);

  const filters: EventFilters = {
    rule: rule.trim() || undefined,
    person_id: personId.trim() ? Number(personId) : undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  };

  const { data, isLoading, error, isFetching } = useQuery({
    queryKey: ["events", filters],
    queryFn: () => api.listEvents(filters),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Events</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Every persisted PPE violation. Newest first.
        </p>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <label className="text-xs font-medium text-muted-foreground">
          Rule
          <Input
            value={rule}
            onChange={(e) => {
              setRule(e.target.value);
              setPage(0);
            }}
            placeholder="vest / helmet / ..."
            className="mt-1 w-44"
          />
        </label>
        <label className="text-xs font-medium text-muted-foreground">
          Worker ID
          <Input
            value={personId}
            onChange={(e) => {
              setPersonId(e.target.value);
              setPage(0);
            }}
            placeholder="e.g. 1"
            inputMode="numeric"
            className="mt-1 w-32"
          />
        </label>
        {isFetching && !isLoading && (
          <span className="text-xs text-muted-foreground">refreshing…</span>
        )}
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-16">ID</TableHead>
              <TableHead>Rule</TableHead>
              <TableHead>Worker</TableHead>
              <TableHead>Class</TableHead>
              <TableHead className="text-right">Conf</TableHead>
              <TableHead className="text-right">Duration</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Ingested</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 8 }).map((__, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : error ? (
              <TableRow>
                <TableCell colSpan={8} className="py-8 text-center text-sm text-destructive">
                  {error.message}
                </TableCell>
              </TableRow>
            ) : !data || data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="py-8 text-center text-sm text-muted-foreground">
                  No events match these filters.
                </TableCell>
              </TableRow>
            ) : (
              data.map((ev) => (
                <TableRow key={ev.id} className="cursor-pointer">
                  <TableCell className="font-mono">
                    <Link href={`/events/${ev.id}`} className="hover:underline">
                      {ev.id}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <RuleBadge rule={ev.rule} />
                  </TableCell>
                  <TableCell className="font-mono">#{ev.person_id}</TableCell>
                  <TableCell className="text-sm">{ev.violation_class}</TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {ev.violation_conf.toFixed(2)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-sm">
                    {ev.duration_seconds.toFixed(1)}s
                  </TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {ev.source ?? "—"}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {new Date(ev.ingested_at).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between text-sm">
        <div className="text-muted-foreground">
          Page {page + 1}
          {data ? ` · showing ${data.length}` : ""}
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-40"
          >
            Prev
          </button>
          <button
            type="button"
            disabled={!data || data.length < PAGE_SIZE}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-md border px-3 py-1.5 text-sm disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
