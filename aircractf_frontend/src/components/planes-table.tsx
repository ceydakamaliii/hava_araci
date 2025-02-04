"use client";

import {
  useReactTable,
  getCoreRowModel,
  createColumnHelper,
  flexRender,
} from "@tanstack/react-table";
import { format } from "date-fns";
import { useState } from "react";
import { CreatePlaneModal } from "./create-plane-modal";

interface Part {
  id: string;
  part_type: string;
  plane_type: string;
  team: string;
  user: {
    id: string;
    email: string;
    first_name: string | null;
    last_name: string | null;
    team_name: string;
    is_active: boolean;
    is_admin: boolean;
  };
  created_at: string;
  updated_at: string;
}

interface Plane {
  id: string;
  plane_type: string;
  parts_used: Part[];
  user: string;
  created_at: string;
}

interface PlanesTableProps {
  planes: Plane[];
  pagination: {
    currentPage: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
    totalCount: number;
  };
  isLoading: boolean;
  onPageChange: (page: number) => void;
}

interface CreatePlaneFormData {
  // Define the structure of the data you'll send to the API
}

interface CreatePlaneResponse {
  error: null | { fallback_message: string };
}

const TableLoadingOverlay = () => (
  <div className="absolute inset-0 bg-white/50 flex items-center justify-center">
    <div className="flex items-center gap-2">
      <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <span className="text-sm text-gray-500">Yükleniyor...</span>
    </div>
  </div>
);

export function PlanesTable({
  planes,
  pagination,
  isLoading,
  onPageChange,
}: PlanesTableProps) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const columnHelper = createColumnHelper<Plane>();

  const handleCreatePlane = async (
    data: CreatePlaneFormData
  ): Promise<CreatePlaneResponse> => {
    const accessToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("access_token="))
      ?.split("=")[1];

    if (!accessToken) {
      return { error: { fallback_message: "No access token found" } };
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/planes/`,
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
      const errorData = await response.json();
      return { error: errorData };
    }

    // Refresh the table
    onPageChange(pagination.currentPage);
    return { error: null };
  };

  const columns = [
    columnHelper.accessor("id", {
      header: "ID",
      cell: (info) => info.getValue().slice(0, 8) + "...",
    }),
    columnHelper.accessor("plane_type", {
      header: "Uçak Tipi",
    }),
    columnHelper.accessor("parts_used", {
      header: "Parça Sayısı",
      cell: (info) => info.getValue().length,
    }),
    columnHelper.accessor("parts_used", {
      id: "parts_details",
      header: "Parça Detayları",
      cell: (info) => (
        <div className="max-w-md">
          {info.getValue().map((part: Part) => (
            <div key={part.id} className="text-xs mb-1">
              <span className="font-semibold">{part.part_type} Parçası</span> -{" "}
              <span className="text-gray-600">{part.plane_type}</span> -{" "}
              <span className="text-gray-500">id: {part.id}</span>
            </div>
          ))}
        </div>
      ),
    }),
    columnHelper.accessor("created_at", {
      header: "Oluşturulma Tarihi",
      cell: (info) => format(new Date(info.getValue()), "dd/MM/yyyy HH:mm"),
    }),
  ];

  const table = useReactTable({
    data: planes,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Uçak Listesi</h2>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              Toplam {pagination.totalCount} uçak
            </span>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
            >
              Yeni Uçak Oluştur
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
                  <tr key={row.id} className="hover:bg-gray-50">
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
      <CreatePlaneModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreatePlane}
      />
    </div>
  );
}
