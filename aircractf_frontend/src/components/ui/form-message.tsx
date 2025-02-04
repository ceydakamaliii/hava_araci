import { cn } from "@/lib/utils";

interface FormMessageProps {
  message?: string;
  className?: string;
}

export function FormMessage({ message, className }: FormMessageProps) {
  if (!message) return null;

  return (
    <p
      className={cn(
        "text-sm font-medium text-destructive animate-shake",
        className
      )}
    >
      {message}
    </p>
  );
}
