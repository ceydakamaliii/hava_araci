"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { FormMessage } from "@/components/ui/form-message";

type TeamType = "WING" | "FUSELAGE" | "TAIL" | "AVIONICS" | "ASSEMBLY";

const TEAM_OPTIONS = [
  { value: "WING" as const, label: "Kanat Takımı" },
  { value: "FUSELAGE" as const, label: "Gövde Takımı" },
  { value: "TAIL" as const, label: "Kuyruk Takımı" },
  { value: "AVIONICS" as const, label: "Aviyonik Takımı" },
  { value: "ASSEMBLY" as const, label: "Montaj Takımı" },
];

interface FormData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  teamName: TeamType;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  firstName?: string;
  lastName?: string;
  teamName?: string;
}

export default function SignupPage() {
  const [formData, setFormData] = useState<FormData>({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    teamName: "WING",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { signup } = useAuth();
  const { toast } = useToast();

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.email) {
      newErrors.email = "Email adresi gereklidir";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Geçerli bir email adresi giriniz";
    }

    if (!formData.firstName?.trim()) {
      newErrors.firstName = "Ad gereklidir";
    }

    if (!formData.lastName?.trim()) {
      newErrors.lastName = "Soyad gereklidir";
    }

    if (!formData.password) {
      newErrors.password = "Şifre gereklidir";
    } else if (formData.password.length < 6) {
      newErrors.password = "Şifre en az 6 karakter olmalıdır";
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Şifrenizi tekrar giriniz";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Şifreler eşleşmiyor";
    }

    if (!formData.teamName) {
      newErrors.teamName = "Lütfen bir takım seçiniz";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handleTeamChange = (value: TeamType) => {
    setFormData((prev) => ({
      ...prev,
      teamName: value,
    }));
    if (errors.teamName) {
      setErrors((prev) => ({
        ...prev,
        teamName: undefined,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      await signup({
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
        team_name: formData.teamName,
      });
      toast({
        title: "Başarılı",
        description: "Hesabınız başarıyla oluşturuldu",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Hata",
        description:
          error.message || "Hesap oluşturulamadı. Lütfen tekrar deneyiniz.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4 relative">
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-50"
        style={{ backgroundImage: "url('/foto2.jpg')" }}
      />
      <Card className="w-full max-w-lg relative z-10">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Hesap Oluştur
          </CardTitle>
          <CardDescription className="text-center">
            Hesap oluşturmak için bilgilerinizi giriniz
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="firstName">Ad</Label>
                  <Input
                    id="firstName"
                    name="firstName"
                    placeholder="Adınızı giriniz"
                    type="text"
                    autoComplete="given-name"
                    value={formData.firstName}
                    onChange={handleChange}
                    className={
                      errors.firstName
                        ? "border-destructive ring-destructive"
                        : ""
                    }
                  />
                  <FormMessage message={errors.firstName} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Soyad</Label>
                  <Input
                    id="lastName"
                    name="lastName"
                    placeholder="Soyadınızı giriniz"
                    type="text"
                    autoComplete="family-name"
                    value={formData.lastName}
                    onChange={handleChange}
                    className={
                      errors.lastName
                        ? "border-destructive ring-destructive"
                        : ""
                    }
                  />
                  <FormMessage message={errors.lastName} />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  placeholder="ornek@ornek.com"
                  type="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={
                    errors.email ? "border-destructive ring-destructive" : ""
                  }
                />
                <FormMessage message={errors.email} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="teamName">Takım</Label>
                <Select
                  value={formData.teamName}
                  onValueChange={handleTeamChange}
                >
                  <SelectTrigger
                    className={
                      errors.teamName
                        ? "border-destructive ring-destructive"
                        : ""
                    }
                  >
                    <SelectValue placeholder="Select your team" />
                  </SelectTrigger>
                  <SelectContent>
                    {TEAM_OPTIONS.map((team) => (
                      <SelectItem key={team.value} value={team.value}>
                        {team.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage message={errors.teamName} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Şifre</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  value={formData.password}
                  onChange={handleChange}
                  className={
                    errors.password ? "border-destructive ring-destructive" : ""
                  }
                />
                <FormMessage message={errors.password} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Şifre Tekrar</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className={
                    errors.confirmPassword
                      ? "border-destructive ring-destructive"
                      : ""
                  }
                />
                <FormMessage message={errors.confirmPassword} />
              </div>
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Hesap oluşturuluyor..." : "Hesap Oluştur"}
            </Button>

            <div className="text-center text-sm">
              Zaten hesabınız var mı?{" "}
              <Link
                href="/login"
                className="text-primary underline-offset-4 hover:underline"
              >
                Giriş Yap
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
