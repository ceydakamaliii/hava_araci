import { useState } from "react";
import * as Select from "@radix-ui/react-select";
import { Check, ChevronDown, Plus, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

const PlaneTypes = {
  TB2: { value: "TB2", label: "TB2" },
  TB3: { value: "TB3", label: "TB3" },
  AKINCI: { value: "AKINCI", label: "AKINCI" },
  KIZILELMA: { value: "KIZILELMA", label: "KIZILELMA" },
} as const;

const PartTypes = {
  WING: { value: "WING", label: "Kanat", minAmount: 2, maxAmount: 2 },
  FUSELAGE: { value: "FUSELAGE", label: "Gövde", minAmount: 1, maxAmount: 1 },
  TAIL: { value: "TAIL", label: "Kuyruk", minAmount: 1, maxAmount: 1 },
  AVIONICS: {
    value: "AVIONICS",
    label: "Aviyonik",
    minAmount: 1,
    maxAmount: null,
  },
} as const;

interface CreatePlaneFormData {
  plane_type: keyof typeof PlaneTypes;
  parts_used: {
    part_type: keyof typeof PartTypes;
    plane_type: keyof typeof PlaneTypes;
    amount: number;
  }[];
}

interface CreatePlaneResponse {
  error: null | {
    detail?: {
      parts_used?: string[];
      non_field_errors?: string[];
    };
    fallback_message?: string;
  };
}

const SelectItem = ({ className, children, ...props }: any) => {
  return (
    <Select.Item
      className={cn(
        "relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-gray-100 focus:text-gray-900 data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        className
      )}
      {...props}
    >
      <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
        <Select.ItemIndicator>
          <Check className="h-4 w-4" />
        </Select.ItemIndicator>
      </span>
      <Select.ItemText>{children}</Select.ItemText>
    </Select.Item>
  );
};

export function CreatePlaneModal({
  isOpen,
  onClose,
  onSubmit,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePlaneFormData) => Promise<CreatePlaneResponse>;
}) {
  const [formData, setFormData] = useState<CreatePlaneFormData>({
    plane_type: "TB2",
    parts_used: [
      { part_type: "WING", plane_type: "TB2", amount: 2 },
      { part_type: "FUSELAGE", plane_type: "TB2", amount: 1 },
      { part_type: "TAIL", plane_type: "TB2", amount: 1 },
      { part_type: "AVIONICS", plane_type: "TB2", amount: 1 },
    ],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handlePlaneTypeChange = (value: keyof typeof PlaneTypes) => {
    setFormData({
      plane_type: value,
      parts_used: formData.parts_used.map((part) => ({
        ...part,
        plane_type: value,
      })),
    });
  };

  const handleAmountChange = (
    partType: keyof typeof PartTypes,
    change: number
  ) => {
    setFormData({
      ...formData,
      parts_used: formData.parts_used.map((part) => {
        if (part.part_type === partType) {
          const minAmount = PartTypes[partType].minAmount;
          const maxAmount = PartTypes[partType].maxAmount;
          const newAmount = part.amount + change;

          // Minimum kontrolü
          if (newAmount < minAmount) return part;

          // Maximum kontrolü (sadece maxAmount tanımlı ise)
          if (maxAmount !== null && newAmount > maxAmount) return part;

          return { ...part, amount: newAmount };
        }
        return part;
      }),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const result = await onSubmit(formData);

    if (result?.error) {
      const errorData = result.error;
      if (errorData.detail?.parts_used) {
        setError(errorData.detail.parts_used[0]);
      } else if (errorData.detail?.non_field_errors) {
        setError(errorData.detail.non_field_errors[0]);
      } else if (errorData.fallback_message) {
        setError(errorData.fallback_message);
      } else {
        setError("Bir hata oluştu");
      }
    } else {
      onClose();
    }

    setIsSubmitting(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Yeni Uçak Oluştur</h2>
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Uçak Tipi
            </label>
            <Select.Root
              value={formData.plane_type}
              onValueChange={handlePlaneTypeChange}
            >
              <Select.Trigger className="flex h-10 w-full items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-950 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                <Select.Value placeholder="Uçak tipi seçin">
                  {PlaneTypes[formData.plane_type].label}
                </Select.Value>
                <Select.Icon>
                  <ChevronDown className="h-4 w-4 opacity-50" />
                </Select.Icon>
              </Select.Trigger>
              <Select.Portal>
                <Select.Content className="relative z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white text-gray-950 shadow-md animate-in fade-in-80">
                  <Select.Viewport className="p-1">
                    {Object.entries(PlaneTypes).map(
                      ([key, { value, label }]) => (
                        <SelectItem key={key} value={value}>
                          {label}
                        </SelectItem>
                      )
                    )}
                  </Select.Viewport>
                </Select.Content>
              </Select.Portal>
            </Select.Root>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Parçalar
            </label>
            <div className="space-y-3">
              {formData.parts_used.map((part) => (
                <div
                  key={part.part_type}
                  className="flex items-center justify-between p-3 border rounded-md"
                >
                  <div>
                    <span className="font-medium">
                      {PartTypes[part.part_type].label}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleAmountChange(part.part_type, -1)}
                      className="p-1 text-gray-500 hover:text-gray-700 disabled:opacity-50"
                      disabled={
                        part.amount <= PartTypes[part.part_type].minAmount
                      }
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <span className="w-8 text-center">{part.amount}</span>
                    <button
                      type="button"
                      onClick={() => handleAmountChange(part.part_type, 1)}
                      className="p-1 text-gray-500 hover:text-gray-700 disabled:opacity-50"
                      disabled={
                        PartTypes[part.part_type].maxAmount !== null &&
                        part.amount >= PartTypes[part.part_type].maxAmount!
                      }
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm border rounded-md hover:bg-gray-50"
              disabled={isSubmitting}
            >
              İptal
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Oluşturuluyor..." : "Oluştur"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
