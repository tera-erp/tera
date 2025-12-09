import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, Loader2, CheckCircle2, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const countryCodes = [
  { code: "ID", name: "Indonesia" },
  { code: "SG", name: "Singapore" },
  { code: "MY", name: "Malaysia" },
  { code: "US", name: "United States" },
  { code: "GB", name: "United Kingdom" },
];

export default function Setup() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [alreadyInitialized, setAlreadyInitialized] = useState(false);
  const [setupInProgress, setSetupInProgress] = useState(false);
  const [setupComplete, setSetupComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
    company_name: "",
    country_code: "ID",
  });

  // Check if setup has already been completed
  useEffect(() => {
    const checkSetupStatus = async () => {
      try {
        const response = await fetch('/api/v1/users/setup/status');
        if (!response.ok) {
          throw new Error('Failed to check setup status');
        }
        const data = await response.json();
        if (data.is_initialized) {
          setAlreadyInitialized(true);
        }
      } catch (err) {
        console.error('Error checking setup status:', err);
      } finally {
        setLoading(false);
      }
    };

    checkSetupStatus();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600 mb-4" />
          <p className="text-gray-600">Checking system status...</p>
        </div>
      </div>
    );
  }

  if (alreadyInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full text-center">
          <div className="flex justify-center mb-4">
            <Lock className="h-16 w-16 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Setup Already Completed
          </h2>
          <p className="text-gray-600 mb-6">
            The system has already been initialized. The setup page is no longer available.
          </p>
          <Button
            onClick={() => navigate("/login")}
            className="w-full bg-blue-600 hover:bg-blue-700"
          >
            Go to Login
          </Button>
        </div>
      </div>
    );
  }

  if (setupComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <div className="flex justify-center mb-4">
            <CheckCircle2 className="h-16 w-16 text-green-500" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Setup Complete!
          </h2>
          <p className="text-gray-600 mb-6">
            Your admin account has been created successfully. Redirecting to
            dashboard...
          </p>
          <Loader2 className="h-6 w-6 animate-spin mx-auto text-blue-600" />
        </div>
      </div>
    );
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCountryChange = (value: string) => {
    setFormData((prev) => ({
      ...prev,
      country_code: value,
    }));
  };

  const validateForm = () => {
    if (!formData.first_name.trim()) {
      setError("First name is required");
      return false;
    }
    if (!formData.last_name.trim()) {
      setError("Last name is required");
      return false;
    }
    if (!formData.email.trim()) {
      setError("Email is required");
      return false;
    }
    if (!formData.email.includes("@")) {
      setError("Invalid email format");
      return false;
    }
    if (!formData.username.trim() || formData.username.length < 3) {
      setError("Username must be at least 3 characters");
      return false;
    }
    if (!formData.password || formData.password.length < 8) {
      setError("Password must be at least 8 characters");
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return false;
    }
    if (!formData.company_name.trim()) {
      setError("Company name is required");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) {
      return;
    }

    setSetupInProgress(true);

    try {
      const response = await fetch("/api/v1/users/setup/admin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          username: formData.username,
          password: formData.password,
          company_name: formData.company_name,
          country_code: formData.country_code,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Setup failed");
      }

      const data = await response.json();
      const { access_token, user } = data;

      // Store credentials
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      setSetupComplete(true);

      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate("/");
        window.location.reload();
      }, 2000);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Setup failed";
      setError(message);
    } finally {
      setSetupInProgress(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 text-center">
            Tera ERP
          </h1>
          <p className="text-center text-gray-600 mt-2">Initial Setup</p>
        </div>

        <p className="text-gray-600 text-sm mb-6 text-center">
          Create your admin account and company to get started
        </p>

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Admin Information */}
          <div className="space-y-2">
            <h3 className="font-semibold text-gray-900 text-sm">
              Admin Account
            </h3>
          </div>

          <div className="space-y-1">
            <Label htmlFor="first_name" className="text-xs font-medium">
              First Name
            </Label>
            <Input
              id="first_name"
              name="first_name"
              type="text"
              placeholder="John"
              value={formData.first_name}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="last_name" className="text-xs font-medium">
              Last Name
            </Label>
            <Input
              id="last_name"
              name="last_name"
              type="text"
              placeholder="Doe"
              value={formData.last_name}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="email" className="text-xs font-medium">
              Email Address
            </Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="admin@company.com"
              value={formData.email}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="username" className="text-xs font-medium">
              Username
            </Label>
            <Input
              id="username"
              name="username"
              type="text"
              placeholder="admin"
              value={formData.username}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="password" className="text-xs font-medium">
              Password
            </Label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="confirmPassword" className="text-xs font-medium">
              Confirm Password
            </Label>
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          {/* Company Information */}
          <div className="space-y-2 pt-4">
            <h3 className="font-semibold text-gray-900 text-sm">
              Company Information
            </h3>
          </div>

          <div className="space-y-1">
            <Label htmlFor="company_name" className="text-xs font-medium">
              Company Name
            </Label>
            <Input
              id="company_name"
              name="company_name"
              type="text"
              placeholder="Your Company Ltd"
              value={formData.company_name}
              onChange={handleChange}
              disabled={loading}
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="country" className="text-xs font-medium">
              Country
            </Label>
            <Select
              value={formData.country_code}
              onValueChange={handleCountryChange}
            >
              <SelectTrigger id="country" disabled={loading}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {countryCodes.map((country) => (
                  <SelectItem key={country.code} value={country.code}>
                    {country.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full mt-6 bg-blue-600 hover:bg-blue-700"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Setting up...
              </>
            ) : (
              "Complete Setup"
            )}
          </Button>
        </form>

        <p className="text-xs text-gray-500 text-center mt-4">
          This is the first-time setup. You can only create an admin account
          once.
        </p>
      </div>
    </div>
  );
}
