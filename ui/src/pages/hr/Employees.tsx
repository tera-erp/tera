import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { ArrowLeft, UserCog, Search, Plus, Eye, Mail, Phone, Calendar, Building2, DollarSign, Loader2, AlertTriangle } from 'lucide-react';
import { useCompany } from '@/context/CompanyContext';
import { useAuth } from '@/context/AuthContext';

interface EmployeeProfile {
  id: number;
  user_id: number;
  company_id: number;
  employee_number: string;
  department: string;
  position: string;
  job_title: string;
  employment_type: string;
  hire_date: string;
  base_salary?: number;
  salary_currency?: string;
  employment_status: string;
  created_at: string;
}

interface Employee {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone?: string;
  status: string;
  company_id: number;
  employee_profile?: EmployeeProfile;
}

const Employees = () => {
  const { activeCompany } = useCompany();
  const { token } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Fetch employees from API
  useEffect(() => {
    const fetchEmployees = async () => {
      if (!token || !activeCompany) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(
          `/api/v1/employees/company/${activeCompany.id}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch employees');
        }

        const data = await response.json();
        setEmployees(data);
        setError(null);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to fetch employees';
        setError(message);
        console.error('Error fetching employees:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEmployees();
  }, [token, activeCompany]);

  const filteredEmployees = employees.filter(emp => {
    const fullName = `${emp.first_name} ${emp.last_name}`.toLowerCase();
    return fullName.includes(searchQuery.toLowerCase()) ||
      emp.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      emp.username.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'on_leave':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
                <UserCog className="h-8 w-8" />
                Employees
              </h1>
              <p className="text-muted-foreground mt-1">
                Manage employee records and profiles
              </p>
            </div>
          </div>
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="mr-2 h-4 w-4" />
            Add Employee
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name, email, or username..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2 text-blue-600" />
              <p className="text-muted-foreground">Loading employees...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <div>
                  <p className="font-semibold text-red-900">Error loading employees</p>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!loading && !error && filteredEmployees.length === 0 && (
          <Card>
            <CardContent className="pt-12 pb-12 text-center">
              <UserCog className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">
                {searchQuery ? 'No employees found matching your search.' : 'No employees yet. Add one to get started.'}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Employees Grid */}
        {!loading && !error && filteredEmployees.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredEmployees.map((employee) => (
              <Card key={employee.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {/* Avatar and Name */}
                    <div className="flex items-start gap-4">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src="" />
                        <AvatarFallback className="bg-blue-600 text-white font-semibold">
                          {getInitials(`${employee.first_name} ${employee.last_name}`)}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="font-semibold text-foreground">{employee.first_name} {employee.last_name}</p>
                        <p className="text-sm text-muted-foreground">@{employee.username}</p>
                      </div>
                    </div>

                    {/* Status Badge */}
                    <Badge className={getStatusColor(employee.status)}>
                      {employee.status}
                    </Badge>

                    {/* Employee Details */}
                    {employee.employee_profile && (
                      <div className="space-y-2 border-t pt-4">
                        <div className="flex items-center gap-2 text-sm">
                          <Building2 className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">{employee.employee_profile.department}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <UserCog className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">{employee.employee_profile.position}</span>
                        </div>
                        {employee.employee_profile.base_salary && (
                          <div className="flex items-center gap-2 text-sm">
                            <DollarSign className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">
                              {employee.employee_profile.base_salary.toLocaleString()} {employee.employee_profile.salary_currency}
                            </span>
                          </div>
                        )}
                        <div className="flex items-center gap-2 text-sm">
                          <Calendar className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">
                            Hired {formatDate(employee.employee_profile.hire_date)}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Contact Info */}
                    <div className="space-y-2 border-t pt-4">
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="h-4 w-4 text-muted-foreground" />
                        <a href={`mailto:${employee.email}`} className="text-blue-600 hover:underline">
                          {employee.email}
                        </a>
                      </div>
                      {employee.phone && (
                        <div className="flex items-center gap-2 text-sm">
                          <Phone className="h-4 w-4 text-muted-foreground" />
                          <a href={`tel:${employee.phone}`} className="text-blue-600 hover:underline">
                            {employee.phone}
                          </a>
                        </div>
                      )}
                    </div>

                    {/* Action Button */}
                    <Dialog open={isDialogOpen && selectedEmployee?.id === employee.id} onOpenChange={setIsDialogOpen}>
                      <DialogTrigger asChild>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full"
                          onClick={() => setSelectedEmployee(employee)}
                        >
                          <Eye className="mr-2 h-4 w-4" />
                          View Details
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>{selectedEmployee?.first_name} {selectedEmployee?.last_name}</DialogTitle>
                          <DialogDescription>Employee profile information</DialogDescription>
                        </DialogHeader>
                        {selectedEmployee && (
                          <div className="space-y-4">
                            <div>
                              <p className="text-sm font-medium">Username</p>
                              <p className="text-sm text-muted-foreground">@{selectedEmployee.username}</p>
                            </div>
                            <div>
                              <p className="text-sm font-medium">Email</p>
                              <p className="text-sm text-muted-foreground">{selectedEmployee.email}</p>
                            </div>
                            {selectedEmployee.phone && (
                              <div>
                                <p className="text-sm font-medium">Phone</p>
                                <p className="text-sm text-muted-foreground">{selectedEmployee.phone}</p>
                              </div>
                            )}
                            {selectedEmployee.employee_profile && (
                              <>
                                <div>
                                  <p className="text-sm font-medium">Employee Number</p>
                                  <p className="text-sm text-muted-foreground">
                                    {selectedEmployee.employee_profile.employee_number}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-sm font-medium">Department</p>
                                  <p className="text-sm text-muted-foreground">
                                    {selectedEmployee.employee_profile.department}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-sm font-medium">Position</p>
                                  <p className="text-sm text-muted-foreground">
                                    {selectedEmployee.employee_profile.position}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-sm font-medium">Employment Type</p>
                                  <p className="text-sm text-muted-foreground">
                                    {selectedEmployee.employee_profile.employment_type}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-sm font-medium">Hire Date</p>
                                  <p className="text-sm text-muted-foreground">
                                    {formatDate(selectedEmployee.employee_profile.hire_date)}
                                  </p>
                                </div>
                                {selectedEmployee.employee_profile.base_salary && (
                                  <div>
                                    <p className="text-sm font-medium">Base Salary</p>
                                    <p className="text-sm text-muted-foreground">
                                      {selectedEmployee.employee_profile.base_salary.toLocaleString()} {selectedEmployee.employee_profile.salary_currency}
                                    </p>
                                  </div>
                                )}
                              </>
                            )}
                          </div>
                        )}
                      </DialogContent>
                    </Dialog>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Stats */}
        {!loading && !error && filteredEmployees.length > 0 && (
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Total Employees</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{employees.length}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Active</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {employees.filter(e => e.status.toLowerCase() === 'active').length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Departments</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {new Set(
                    employees
                      .filter(e => e.employee_profile)
                      .map(e => e.employee_profile!.department)
                  ).size}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default Employees;
