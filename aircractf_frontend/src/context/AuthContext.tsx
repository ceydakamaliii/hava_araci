"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { useToast } from "@/hooks/use-toast";

interface User {
  email: string;
  first_name?: string;
  last_name?: string;
  team_name?: string;
}

interface SignUpData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  team_name: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: SignUpData) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Kimlik doğrulama gerektiren korumalı rotalar
const PROTECTED_ROUTES = ["/dashboard", "/profile", "/settings"];
// Kimlik doğrulama gerektirmeyen genel rotalar
const PUBLIC_ROUTES = ["/", "/login", "/signup"];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  // Kimlik doğrulama durumunu kontrol et
  const checkAuth = () => {
    const accessToken = Cookies.get("access_token");
    const refreshToken = Cookies.get("refresh_token");
    return !!(accessToken && refreshToken);
  };

  // Token'ları doğrula ve kullanıcı verilerini getir
  const verifyAuth = async () => {
    try {
      const accessToken = Cookies.get("access_token");
      if (!accessToken) {
        // Erişim token'ı yoksa, yenilemeyi dene
        return await refreshToken();
      }

      // Mevcut erişim token'ını kullanmayı dene
      const response = await fetch(`${API_URL}/v1/users/me/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        credentials: "include",
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
        return true;
      } else {
        console.log("Erişim token'ının süresi dolmuş, yenileme deneniyor...");
        // Erişim token'ı geçersiz/süresi dolmuşsa, yenilemeyi dene
        return await refreshToken();
      }
    } catch (error) {
      console.error("Kimlik doğrulama başarısız oldu:", error);
      // Son çare olarak token yenilemeyi dene
      return await refreshToken();
    }
  };

  // Token'ı yenile
  const refreshToken = async () => {
    try {
      const refresh = Cookies.get("refresh_token");
      if (!refresh) {
        console.log("Yenileme token'ı bulunamadı");
        await logout();
        return false;
      }

      console.log("Token yenileme deneniyor...");
      const response = await fetch(`${API_URL}/v1/users/token/refresh/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh }),
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        console.log(
          "Token başarıyla yenilendi, yeni erişim token'ı ayarlanıyor"
        );

        // Yeni erişim token'ını uygun seçeneklerle cookie'lere kaydet
        Cookies.set("access_token", data.access, {
          secure: true,
          sameSite: "strict",
          path: "/", // Token'ın tüm yollarda kullanılabilir olmasını sağla
        });

        // Yeni token ile kullanıcı verilerini getir
        const userResponse = await fetch(`${API_URL}/v1/users/me/`, {
          headers: {
            Authorization: `Bearer ${data.access}`,
          },
          credentials: "include",
        });

        if (userResponse.ok) {
          const userData = await userResponse.json();
          console.log("Yeni token ile kullanıcı verileri getirildi");
          setUser(userData);
          setIsAuthenticated(true);
          return true;
        } else {
          console.error("Yeni token ile kullanıcı verileri getirilemedi");
          return false;
        }
      }

      // Token yenileme başarısız olduysa çıkış yap
      console.log("Token yenileme başarısız oldu - çıkış yapılıyor");
      await logout();
      return false;
    } catch (error) {
      console.error("Token yenileme başarısız oldu:", error);
      await logout();
      return false;
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/v1/users/token/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        toast({
          variant: "destructive",
          title: "Giriş Başarısız",
          description:
            errorData.detail ||
            "Giriş yapılamadı. Lütfen email ve şifrenizi kontrol edin.",
        });
        return;
      }

      const data = await response.json();

      // Set tokens in cookies
      Cookies.set("access_token", data.access, {
        secure: true,
        sameSite: "strict",
      });
      Cookies.set("refresh_token", data.refresh, {
        secure: true,
        sameSite: "strict",
      });

      // Fetch user data
      const userResponse = await fetch(`${API_URL}/v1/users/me/`, {
        headers: {
          Authorization: `Bearer ${data.access}`,
        },
        credentials: "include",
      });

      if (!userResponse.ok) {
        toast({
          variant: "destructive",
          title: "Hata",
          description: "Kullanıcı bilgileri alınamadı. Lütfen tekrar deneyin.",
        });
        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
        setIsAuthenticated(false);
        return;
      }

      const userData = await userResponse.json();
      setUser(userData);
      setIsAuthenticated(true);

      toast({
        title: "Başarılı",
        description: "Giriş başarıyla yapıldı.",
      });

      // Force navigation after state updates
      setTimeout(() => {
        router.push("/dashboard");
      }, 100);
    } catch (error: any) {
      console.error("Login failed:", error);
      Cookies.remove("access_token");
      Cookies.remove("refresh_token");
      setIsAuthenticated(false);
      toast({
        variant: "destructive",
        title: "Hata",
        description: "Bir hata oluştu. Lütfen tekrar deneyin.",
      });
    }
  };

  // Rota koruması ile anında kontrol
  useEffect(() => {
    const checkRouteAccess = () => {
      if (!isLoading) {
        const currentPath = window.location.pathname;
        console.log("Rota kontrolü:", {
          currentPath,
          isAuthenticated,
          isLoading,
          user: !!user,
        });

        if (PROTECTED_ROUTES.includes(currentPath)) {
          if (!isAuthenticated) {
            console.log("Erişim reddedildi - giriş sayfasına yönlendiriliyor");
            router.push("/login");
          }
        } else if (PUBLIC_ROUTES.includes(currentPath)) {
          if (isAuthenticated) {
            console.log(
              "Kimliği doğrulanmış kullanıcı genel rotaya erişiyor - gösterge paneline yönlendiriliyor"
            );
            router.push("/dashboard");
          }
        }
      }
    };

    checkRouteAccess();
  }, [isAuthenticated, isLoading, router, user]);

  // İlk kimlik doğrulama kontrolü
  useEffect(() => {
    const initAuth = async () => {
      try {
        console.log("Kimlik doğrulama kontrolü başlatılıyor");
        if (checkAuth()) {
          console.log("Token'lar bulundu, doğrulanıyor...");
          const isValid = await verifyAuth();
          if (!isValid) {
            console.log("Token doğrulama başarısız oldu, çıkış yapılıyor");
            await logout();
          } else {
            console.log("Token doğrulama başarılı");
            const currentPath = window.location.pathname;
            if (PUBLIC_ROUTES.includes(currentPath)) {
              console.log(
                "Kimliği doğrulanmış kullanıcı genel rotadan yönlendiriliyor"
              );
              router.push("/dashboard");
            }
          }
        } else {
          console.log("Token bulunamadı");
          const currentPath = window.location.pathname;
          if (PROTECTED_ROUTES.includes(currentPath)) {
            console.log(
              "Kimliği doğrulanmamış kullanıcı korumalı rotadan yönlendiriliyor"
            );
            router.push("/login");
          }
        }
      } catch (error) {
        console.error("Kimlik doğrulama başlatma hatası:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const signup = async (data: SignUpData) => {
    try {
      const response = await fetch(`${API_URL}/v1/users/sign-up/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        credentials: "include",
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        toast({
          variant: "destructive",
          title: "Kayıt Başarısız",
          description:
            errorData.message ||
            "Kayıt oluşturulamadı. Lütfen bilgilerinizi kontrol edin.",
        });
        return;
      }

      const userData = await response.json();

      // Set tokens in cookies
      if (userData.tokens) {
        Cookies.set("access_token", userData.tokens.access, {
          secure: true,
          sameSite: "strict",
        });
        Cookies.set("refresh_token", userData.tokens.refresh, {
          secure: true,
          sameSite: "strict",
        });
      }

      setUser(userData.user);
      setIsAuthenticated(true);

      toast({
        title: "Başarılı",
        description: "Hesabınız başarıyla oluşturuldu.",
      });

      router.push("/dashboard");
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Hata",
        description:
          "Kayıt işlemi sırasında bir hata oluştu. Lütfen tekrar deneyin.",
      });
    }
  };

  const logout = async () => {
    try {
      const refreshToken = Cookies.get("refresh_token");
      const accessToken = Cookies.get("access_token");

      if (refreshToken && accessToken) {
        const response = await fetch(`${API_URL}/v1/users/logout/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          credentials: "include",
          body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!response.ok) {
          toast({
            variant: "destructive",
            title: "Hata",
            description: "Çıkış yapılırken bir sorun oluştu.",
          });
        }
      }
    } catch (error) {
      console.error("Logout error:", error);
      toast({
        variant: "destructive",
        title: "Hata",
        description: "Çıkış yapılırken bir hata oluştu.",
      });
    } finally {
      // user data ve tokenı sil
      Cookies.remove("access_token");
      Cookies.remove("refresh_token");
      setUser(null);
      setIsAuthenticated(false);

      toast({
        title: "Başarılı",
        description: "Başarıyla çıkış yapıldı.",
      });

      router.push("/login");
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, login, signup, logout, isLoading, isAuthenticated }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth, bir AuthProvider içinde kullanılmalıdır");
  }
  return context;
}
