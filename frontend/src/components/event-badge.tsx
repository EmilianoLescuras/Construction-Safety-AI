import { Badge } from "@/components/ui/badge";

const RULE_COLORS: Record<string, string> = {
  vest: "bg-red-500/15 text-red-700 dark:text-red-300",
  helmet: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  mask: "bg-sky-500/15 text-sky-700 dark:text-sky-300",
};

export function RuleBadge({ rule }: { rule: string }) {
  const cls = RULE_COLORS[rule] ?? "bg-muted text-foreground";
  return (
    <Badge variant="secondary" className={cls + " uppercase"}>
      {rule}
    </Badge>
  );
}

export function SinkBadge({
  sink,
  success,
}: {
  sink: string;
  success: boolean;
}) {
  return (
    <Badge
      variant="outline"
      className={
        success
          ? "border-emerald-500/40 text-emerald-700 dark:text-emerald-300"
          : "border-destructive/50 text-destructive"
      }
    >
      {sink}
      {success ? " ok" : " fail"}
    </Badge>
  );
}
