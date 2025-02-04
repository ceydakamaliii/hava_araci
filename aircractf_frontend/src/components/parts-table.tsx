"use client";

import {
  useReactTable,
  getCoreRowModel,
  createColumnHelper,
  flexRender,
} from "@tanstack/react-table";
import { format } from "date-fns";
import { useState } from "react";
import * as Select from "@radix-ui/react-select";
import { Check, ChevronDown, Trash2, Plus, Minus } from "lucide-react";
import { cn } from "@/lib/utils";
import React from "react";
import { useToast } from "@/hooks/use-toast";

interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  team_name: string;
  is_active: boolean;
  is_admin: boolean;
}

interface Part {
  id: string;
  part_type: string;
  plane_type: string;
  team: string;
  user: User;
  created_at: string;
  updated_at: string;
  used_in_plane: boolean;
  part_usages: PartUsage[];
}

interface PartUsage {
  plane_assembly?: string;
}

interface PartsTableProps {
  parts: Part[];
  pagination: {
    currentPage: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
    totalCount: number;
  };
  isLoading: boolean;
  onPageChange: (page: number) => void;
  userTeam: string;
  onScoreUpdate: () => void;
}

const PartTypes = {
  WING: { value: "WING", label: "Kanat" },
  FUSELAGE: { value: "FUSELAGE", label: "Gövde" },
  TAIL: { value: "TAIL", label: "Kuyruk" },
  AVIONICS: { value: "AVIONICS", label: "Aviyonik" },
} as const;

const PlaneTypes = {
  TB2: { value: "TB2", label: "TB2" },
  TB3: { value: "TB3", label: "TB3" },
  AKINCI: { value: "AKINCI", label: "AKINCI" },
  KIZILELMA: { value: "KIZILELMA", label: "KIZILELMA" },
} as const;

interface CreatePartFormData {
  part_type: keyof typeof PartTypes;
  plane_type: keyof typeof PlaneTypes;
  quantity: number;
}

const SelectItem = React.forwardRef<
  React.ElementRef<typeof Select.Item>,
  React.ComponentPropsWithoutRef<typeof Select.Item>
>(({ className, children, ...props }, ref) => {
  return (
    <Select.Item
      ref={ref}
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
});
SelectItem.displayName = "SelectItem";

const CreatePartModal = ({
  isOpen,
  onClose,
  onSubmit,
  userTeam,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePartFormData) => Promise<void>;
  userTeam: string;
}) => {
  const [formData, setFormData] = useState<CreatePartFormData>({
    part_type: userTeam as keyof typeof PartTypes,
    plane_type: "TB2",
    quantity: 1,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error("Error creating part:", error);

      if (error instanceof Error) {
        try {
          const errorData = JSON.parse(error.message);
          if (errorData.detail?.non_field_errors) {
            setError(errorData.detail.non_field_errors[0]);
          } else if (errorData.fallback_message) {
            setError(errorData.fallback_message);
          } else {
            setError("Bir hata oluştu");
          }
        } catch {
          setError("Bir hata oluştu");
        }
      } else {
        setError("Bir hata oluştu");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAmountChange = (change: number) => {
    const newAmount = formData.quantity + change;
    // Miktar 1'den az olamaz
    if (newAmount >= 1) {
      setFormData({ ...formData, quantity: newAmount });
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Yeni Parça Oluştur</h2>
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Parça Tipi
            </label>
            <Select.Root
              value={formData.part_type}
              onValueChange={(value: keyof typeof PartTypes) =>
                setFormData({ ...formData, part_type: value })
              }
            >
              <Select.Trigger className="flex h-10 w-full items-center justify-between rounded-md border border-gray-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-950 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                <Select.Value placeholder="Parça tipi seçin">
                  {PartTypes[formData.part_type].label}
                </Select.Value>
                <Select.Icon>
                  <ChevronDown className="h-4 w-4 opacity-50" />
                </Select.Icon>
              </Select.Trigger>
              <Select.Portal>
                <Select.Content className="relative z-50 min-w-[8rem] overflow-hidden rounded-md border bg-white text-gray-950 shadow-md animate-in fade-in-80">
                  <Select.Viewport className="p-1">
                    {Object.entries(PartTypes).map(
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
            <p className="mt-1 text-sm text-gray-500">
              Şu anda{" "}
              {PartTypes[userTeam as keyof typeof PartTypes]?.label || userTeam}{" "}
              ekibindesiniz.
            </p>
          </div>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Uçak Tipi
            </label>
            <Select.Root
              value={formData.plane_type}
              onValueChange={(value: keyof typeof PlaneTypes) =>
                setFormData({ ...formData, plane_type: value })
              }
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kaç adet üretilecek
            </label>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handleAmountChange(-1)}
                className="p-1 text-gray-500 hover:text-gray-700 disabled:opacity-50"
                disabled={formData.quantity <= 1}
              >
                <Minus className="w-4 h-4" />
              </button>
              <span className="w-8 text-center">{formData.quantity}</span>{" "}
              <button
                type="button"
                onClick={() => handleAmountChange(1)}
                className="p-1 text-gray-500 hover:text-gray-700"
              >
                <Plus className="w-4 h-4" />
              </button>
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
};

const DeleteConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  isDeleting,
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  isDeleting: boolean;
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Parçayı Sil</h2>
        <p className="text-gray-600 mb-6">
          Bu parçayı silmek istediğinize emin misiniz?
        </p>
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm border rounded-md hover:bg-gray-50"
            disabled={isDeleting}
          >
            İptal
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            disabled={isDeleting}
          >
            {isDeleting ? "Siliniyor..." : "Sil"}
          </button>
        </div>
      </div>
    </div>
  );
};

const TableLoadingOverlay = () => (
  <div className="absolute inset-0 bg-white/50 flex items-center justify-center">
    <div className="flex items-center gap-2">
      <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <span className="text-sm text-gray-500">Yükleniyor...</span>
    </div>
  </div>
);

export function PartsTable({
  parts,
  pagination,
  isLoading,
  onPageChange,
  userTeam,
  onScoreUpdate,
}: PartsTableProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedPartId, setSelectedPartId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const columnHelper = createColumnHelper<Part>();
  const { toast } = useToast();

  const handleCreatePart = async (data: CreatePartFormData) => {
    const accessToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("access_token="))
      ?.split("=")[1];

    if (!accessToken) {
      toast({
        variant: "destructive",
        title: "Hata",
        description: "Oturum bilgisi bulunamadı. Lütfen tekrar giriş yapın.",
      });
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/parts/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify(data),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        if (error.detail?.non_field_errors) {
          toast({
            variant: "destructive",
            title: "Hata",
            description: error.detail.non_field_errors[0],
          });
        } else if (error.fallback_message) {
          toast({
            variant: "destructive",
            title: "Hata",
            description: error.fallback_message,
          });
        } else {
          toast({
            variant: "destructive",
            title: "Hata",
            description:
              "Parça oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.",
          });
        }
        return;
      }

      toast({
        title: "Başarılı",
        description: "Parça başarıyla oluşturuldu.",
      });

      // Refresh the table
      onScoreUpdate();
      onPageChange(pagination.currentPage);
      setIsModalOpen(false);
    } catch (error) {
      console.error("Error creating part:", error);
      toast({
        variant: "destructive",
        title: "Hata",
        description:
          "Parça oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.",
      });
    }
  };

  const handleDeletePart = async () => {
    if (!selectedPartId) return;

    try {
      setIsDeleting(true);
      const accessToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];

      if (!accessToken) {
        toast({
          variant: "destructive",
          title: "Hata",
          description: "Oturum bilgisi bulunamadı. Lütfen tekrar giriş yapın.",
        });
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/parts/${selectedPartId}/`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) {
        const error = await response.json();
        if (error.detail?.non_field_errors) {
          toast({
            variant: "destructive",
            title: "Hata",
            description: error.detail.non_field_errors[0],
          });
        } else if (error.fallback_message) {
          toast({
            variant: "destructive",
            title: "Hata",
            description: error.fallback_message,
          });
        } else {
          toast({
            variant: "destructive",
            title: "Hata",
            description:
              "Parça silinirken bir hata oluştu. Lütfen tekrar deneyin.",
          });
        }
        return;
      }

      toast({
        title: "Başarılı",
        description: "Parça başarıyla silindi.",
      });

      // Refresh the table
      onScoreUpdate();
      onPageChange(pagination.currentPage);
      setIsDeleteModalOpen(false);
    } catch (error) {
      console.error("Error deleting part:", error);
      toast({
        variant: "destructive",
        title: "Hata",
        description: "Parça silinirken bir hata oluştu. Lütfen tekrar deneyin.",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const columns = [
    columnHelper.accessor("id", {
      header: "ID",
      cell: (info) => info.getValue().slice(0, 8) + "...",
    }),
    columnHelper.accessor("part_type", {
      header: "Parça Tipi",
    }),
    columnHelper.accessor("plane_type", {
      header: "Uçak Tipi",
    }),
    columnHelper.accessor("team", {
      header: "Takım",
    }),
    columnHelper.accessor("user", {
      header: "Üreten Kişi",
      cell: (info) => {
        const user = info.getValue();
        return user.email;
      },
    }),
    columnHelper.accessor("created_at", {
      header: "Oluşturulma Tarihi",
      cell: (info) => format(new Date(info.getValue()), "dd/MM/yyyy HH:mm"),
    }),
    columnHelper.accessor("used_in_plane", {
      header: "Durum",
      cell: (info) => {
        const part = info.row.original;
        return (
          <div className="flex items-center gap-1">
            {info.getValue() ? (
              <div className="flex flex-col">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Uçakta Kullanılıyor
                </span>
                {part.part_usages?.length > 0 &&
                  part.part_usages[0].plane_assembly && (
                    <span className="text-xs text-gray-500 mt-1 px-2">
                      Uçak: {part.part_usages[0].plane_assembly}
                    </span>
                  )}
              </div>
            ) : (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Depoda
              </span>
            )}
          </div>
        );
      },
    }),
    columnHelper.display({
      id: "actions",
      header: "",
      cell: (info) => {
        const part = info.row.original;
        return (
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setSelectedPartId(part.id);
                setIsDeleteModalOpen(true);
              }}
              className="p-1 text-gray-500 hover:text-red-600 rounded-md hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
              title={
                part.used_in_plane ? "Uçakta kullanılan parça silinemez" : "Sil"
              }
              disabled={part.used_in_plane}
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        );
      },
    }),
  ];

  const table = useReactTable({
    data: parts,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">
            Parça Listesi (
            {userTeam === "WING"
              ? "Kanat"
              : userTeam === "TAIL"
              ? "Kuyruk"
              : userTeam === "FUSELAGE"
              ? "Gövde"
              : userTeam === "AVIONICS"
              ? "Aviyonik"
              : ""}{" "}
            Parçası )
          </h2>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              Toplam {pagination.totalCount} parça
            </span>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
            >
              Yeni Parça Ekle
            </button>
          </div>
        </div>
        <div className="relative">
          {isLoading && <TableLoadingOverlay />}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className={cn(
                      "hover:bg-gray-50 transition-colors",
                      row.original.used_in_plane && "bg-blue-50/50"
                    )}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="mt-4 flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={() => onPageChange(pagination.currentPage - 1)}
              disabled={!pagination.hasPrevious || isLoading}
              className="px-3 py-1 border rounded text-sm disabled:opacity-50"
            >
              Önceki
            </button>
            <button
              onClick={() => onPageChange(pagination.currentPage + 1)}
              disabled={!pagination.hasNext || isLoading}
              className="px-3 py-1 border rounded text-sm disabled:opacity-50"
            >
              Sonraki
            </button>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-700">
              Sayfa {pagination.currentPage} / {pagination.totalPages}
            </span>
          </div>
        </div>
      </div>
      <DeleteConfirmationModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDeletePart}
        isDeleting={isDeleting}
      />
      <CreatePartModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreatePart}
        userTeam={userTeam}
      />
    </div>
  );
}
