"use client";

import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PlanesTable } from "@/components/planes-table";
import { PartsTable } from "@/components/parts-table";
import { PartScoreCards } from "@/components/part-score-cards";
import { useToast } from "@/hooks/use-toast";

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
  used_in_plane: boolean;
  part_usages: PartUsage[];
}

interface PartUsage {
  plane_assembly?: string;
}

interface Plane {
  id: string;
  plane_type: string;
  parts_used: Part[];
  user: string;
  created_at: string;
}

interface PlanesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Plane[];
}

interface PartsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Part[];
}
export interface PartScoreType {
  team: string;
  part_type: string;
  scores: Scores;
}

interface Scores {
  TB2: {
    used: number;
    unused: number;
  };
  TB3: {
    used: number;
    unused: number;
  };
  AKINCI: {
    used: number;
    unused: number;
  };
  KIZILELMA: {
    used: number;
    unused: number;
  };
}

export default function DashboardPage() {
  const { user, logout, isLoading } = useAuth();
  const [isMounted, setIsMounted] = useState(false);
  const [planes, setPlanes] = useState<Plane[]>([]);
  const [parts, setParts] = useState<Part[]>([]);
  const [score, setScore] = useState<PartScoreType>();
  const [isLoadingPlanes, setIsLoadingPlanes] = useState(true);
  const [isLoadingParts, setIsLoadingParts] = useState(true);
  const [isLoadingScores, setIsLoadingScores] = useState(true);
  const [planesPagination, setPlanesPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    hasNext: false,
    hasPrevious: false,
    totalCount: 0,
  });
  const [partsPagination, setPartsPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    hasNext: false,
    hasPrevious: false,
    totalCount: 0,
  });
  const router = useRouter();
  const { toast } = useToast();

  const fetchPlanes = async (page: number = 1) => {
    try {
      setIsLoadingPlanes(true);
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
        `${process.env.NEXT_PUBLIC_API_URL}/v1/planes/?page=${page}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) {
        toast({
          variant: "destructive",
          title: "Hata",
          description: "Uçak bilgileri getirilemedi. Lütfen tekrar deneyin.",
        });
        return;
      }

      const data: PlanesResponse = await response.json();
      setPlanes(data.results);
      setPlanesPagination({
        currentPage: page,
        totalPages: Math.ceil(data.count / 10),
        hasNext: !!data.next,
        hasPrevious: !!data.previous,
        totalCount: data.count,
      });
    } catch (error) {
      console.error("Error fetching planes:", error);
      toast({
        variant: "destructive",
        title: "Hata",
        description: "Uçak bilgileri yüklenirken bir hata oluştu.",
      });
    } finally {
      setIsLoadingPlanes(false);
    }
  };

  const fetchParts = async (page: number = 1) => {
    try {
      setIsLoadingParts(true);
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
        `${process.env.NEXT_PUBLIC_API_URL}/v1/parts/?page=${page}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) {
        toast({
          variant: "destructive",
          title: "Hata",
          description: "Parça bilgileri getirilemedi. Lütfen tekrar deneyin.",
        });
        return;
      }

      const data: PartsResponse = await response.json();
      setParts(data.results);
      setPartsPagination({
        currentPage: page,
        totalPages: Math.ceil(data.count / 10),
        hasNext: !!data.next,
        hasPrevious: !!data.previous,
        totalCount: data.count,
      });
    } catch (error) {
      console.error("Error fetching parts:", error);
      toast({
        variant: "destructive",
        title: "Hata",
        description: "Parça bilgileri yüklenirken bir hata oluştu.",
      });
    } finally {
      setIsLoadingParts(false);
    }
  };

  const fetchScores = async () => {
    try {
      setIsLoadingScores(true);
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
        `${process.env.NEXT_PUBLIC_API_URL}/v1/parts/score/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) {
        toast({
          variant: "destructive",
          title: "Hata",
          description: "Skor bilgileri getirilemedi. Lütfen tekrar deneyin.",
        });
        return;
      }

      const data: PartScoreType = await response.json();
      setScore(data);
    } catch (error) {
      console.error("Error fetching scores:", error);
      toast({
        variant: "destructive",
        title: "Hata",
        description: "Skor bilgileri yüklenirken bir hata oluştu.",
      });
    } finally {
      setIsLoadingScores(false);
    }
  };

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user) {
      if (user.team_name === "ASSEMBLY") {
        fetchPlanes(1);
      } else {
        fetchParts(1);
        fetchScores();
      }
    }
  }, [user]);

  if (!isMounted || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Giriş yapmaya yönlendiriliyorsunuz...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Gösterge Paneli</h1>
            </div>
            <div className="flex items-center">
              {user && (
                <>
                  <span className="mr-4">Hoşgeldin, {user.email}</span>
                  <span className="mr-4">
                    Takım:{" "}
                    {user.team_name === "WING"
                      ? "Kanat"
                      : user.team_name === "TAIL"
                      ? "Kuyruk"
                      : user.team_name === "FUSELAGE"
                      ? "Gövde"
                      : user.team_name === "AVIONICS"
                      ? "Aviyonik"
                      : user.team_name === "ASSEMBLY"
                      ? "Montaj"
                      : ""}{" "}
                  </span>
                </>
              )}
              <button
                onClick={() => logout()}
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Çıkış Yap
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {user &&
            (user.team_name === "ASSEMBLY" ? (
              <PlanesTable
                planes={planes}
                pagination={planesPagination}
                isLoading={isLoadingPlanes}
                onPageChange={fetchPlanes}
              />
            ) : (
              <>
                <PartScoreCards score={score} isLoading={isLoadingScores} />
                <PartsTable
                  parts={parts}
                  pagination={partsPagination}
                  isLoading={isLoadingParts}
                  onPageChange={fetchParts}
                  userTeam={user.team_name || ""}
                  onScoreUpdate={fetchScores}
                />
              </>
            ))}
        </div>
      </main>
    </div>
  );
}
