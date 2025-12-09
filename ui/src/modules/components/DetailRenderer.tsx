import React, { useState, useEffect } from 'react';
import { ScreenConfig, WorkflowConfig, FormConfig } from '../types';
import { FormRenderer } from './FormRenderer';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, ArrowLeft, Loader2, Edit2, Trash2 } from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface DetailRendererProps {
  config: ScreenConfig;
  formConfig?: FormConfig;
  recordId: string;
  data?: any;
  loading?: boolean;
  submitLoading?: boolean;
  deleteLoading?: boolean;
  error?: string;
  isCreating?: boolean;
  workflow?: WorkflowConfig;
  workflowState?: string;
  onBack?: () => void;
  onEdit?: (data: any) => Promise<void>;
  onDelete?: () => Promise<void>;
  onWorkflowTransition?: (transitionKey: string) => Promise<void>;
  readOnly?: boolean;
  editMode?: boolean;
  onEditModeChange?: (editing: boolean) => void;
}

export const DetailRenderer: React.FC<DetailRendererProps> = ({
  config,
  formConfig,
  recordId,
  data,
  loading = false,
  submitLoading = false,
  deleteLoading = false,
  error,
  isCreating = false,
  workflow,
  workflowState,
  onBack,
  onEdit,
  onDelete,
  onWorkflowTransition,
  readOnly = false,
  editMode = false,
  onEditModeChange,
}) => {
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const detailConfig = config.detail_config;

  const handleDelete = async () => {
    if (!onDelete) return;
    try {
      setIsDeleting(true);
      await onDelete();
    } finally {
      setIsDeleting(false);
      setDeleteConfirm(false);
    }
  };

  const handleEditSubmit = async (formData: any) => {
    if (onEdit) {
      await onEdit(formData);
      onEditModeChange?.(false);
    }
  };

  if (loading && !isCreating) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex gap-2 items-center">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (error && !isCreating) {
    return (
      <div className="space-y-4">
        {onBack && (
          <Button variant="outline" onClick={onBack} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
        )}
        <Card>
          <CardContent className="pt-6">
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 flex gap-3">
              <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
              <p className="text-sm text-destructive">{error || 'Record not found'}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

      {/* For create mode, show form immediately */}
      if (isCreating && formConfig) {
        return (
          <FormRenderer
            config={formConfig}
            initialData={{}}
            onSubmit={handleEditSubmit}
            onCancel={onBack}
            loading={submitLoading}
            readOnly={false}
            isEditing={false}
          />
        );
      }  if (!data && !isCreating) {
    return (
      <div className="space-y-4">
        {onBack && (
          <Button variant="outline" onClick={onBack} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
        )}
        <Card>
          <CardContent className="pt-6">
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 flex gap-3">
              <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
              <p className="text-sm text-destructive">Record not found</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with navigation and actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {onBack && (
            <Button variant="outline" size="sm" onClick={onBack}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
          )}
          <div>
            <h1 className="text-2xl font-bold">{config.title}</h1>
            <p className="text-sm text-muted-foreground">ID: {recordId}</p>
          </div>
        </div>

        <div className="flex gap-2">
          {!editMode && !readOnly && onEdit && (
            <Button
              onClick={() => onEditModeChange?.(true)}
              variant="outline"
              className="gap-2"
              disabled={submitLoading}
            >
              <Edit2 className="h-4 w-4" />
              Edit
            </Button>
          )}
          {!editMode && onDelete && (
            <Button
              onClick={() => setDeleteConfirm(true)}
              variant="destructive"
              className="gap-2"
              disabled={deleteLoading}
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </Button>
          )}
        </div>
      </div>

      {/* Main content area */}
      <div className={`grid gap-4 ${detailConfig?.sidebar ? 'lg:grid-cols-3' : ''}`}>
        {/* Main column */}
        <div className={detailConfig?.sidebar ? 'lg:col-span-2' : ''}>
          {editMode && formConfig ? (
            // Edit form
            <FormRenderer
              config={formConfig}
              initialData={data}
              onSubmit={handleEditSubmit}
              onCancel={() => onEditModeChange?.(false)}
              readOnly={false}
              loading={submitLoading}
              isEditing={true}
              workflowState={workflowState}
            />
          ) : (
            // Display mode - with better field formatting
            <div className="space-y-4">
              {/* Summary card for key fields */}
              {(data?.name || data?.first_name) && (
                <Card className="border-2 border-blue-100 bg-blue-50/30">
                  <CardHeader>
                    <CardTitle className="text-xl">
                      {data?.name || `${data?.first_name} ${data?.last_name || ''}`.trim()}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {data?.email && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Email</span>
                        <a href={`mailto:${data.email}`} className="text-sm font-medium text-blue-600 hover:underline">
                          {data.email}
                        </a>
                      </div>
                    )}
                    {data?.employee_number && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Employee #</span>
                        <span className="text-sm font-medium">{data.employee_number}</span>
                      </div>
                    )}
                    {data?.status && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Status</span>
                        <Badge variant={data.status === 'active' ? 'default' : 'secondary'}>
                          {data.status}
                        </Badge>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Employment Details */}
              {(data?.department || data?.position || data?.employment_type || data?.hire_date) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Employment Details</CardTitle>
                  </CardHeader>
                  <CardContent className="grid grid-cols-2 gap-4">
                    {data?.department && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Department</p>
                        <p className="text-sm font-medium">{data.department}</p>
                      </div>
                    )}
                    {data?.position && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Position</p>
                        <p className="text-sm font-medium">{data.position}</p>
                      </div>
                    )}
                    {data?.employment_type && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Employment Type</p>
                        <Badge variant="outline" className="capitalize">
                          {data.employment_type.replace(/_/g, ' ')}
                        </Badge>
                      </div>
                    )}
                    {data?.hire_date && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Hire Date</p>
                        <p className="text-sm font-medium">
                          {new Date(data.hire_date).toLocaleDateString()}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Compensation */}
              {(data?.base_salary || data?.salary_currency) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Compensation</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {data?.base_salary && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Base Salary</span>
                        <span className="text-sm font-medium">
                          {Number(data.base_salary).toLocaleString()} {data.salary_currency || 'USD'}
                        </span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Personal Information */}
              {(data?.date_of_birth || data?.mobile_phone) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Personal Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {data?.date_of_birth && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Date of Birth</span>
                        <span className="text-sm font-medium">
                          {new Date(data.date_of_birth).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    {data?.mobile_phone && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Mobile Phone</span>
                        <a href={`tel:${data.mobile_phone}`} className="text-sm font-medium text-blue-600 hover:underline">
                          {data.mobile_phone}
                        </a>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Banking Information */}
              {(data?.bank_account_number || data?.bank_account_holder || data?.bank_name) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Banking Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {data?.bank_account_number && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Account Number</span>
                        <span className="text-sm font-medium font-mono">{data.bank_account_number}</span>
                      </div>
                    )}
                    {data?.bank_account_holder && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Account Holder</span>
                        <span className="text-sm font-medium">{data.bank_account_holder}</span>
                      </div>
                    )}
                    {data?.bank_name && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Bank Name</span>
                        <span className="text-sm font-medium">{data.bank_name}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Additional Information */}
              {Object.entries(data || {}).filter(([key]) => {
                // Filter out already displayed fields
                const displayedFields = [
                  'name', 'first_name', 'last_name', 'email', 'employee_number', 'status',
                  'department', 'position', 'employment_type', 'hire_date',
                  'base_salary', 'salary_currency', 'date_of_birth', 'mobile_phone',
                  'bank_account_number', 'bank_account_holder', 'bank_name',
                  'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
                ];
                return !displayedFields.includes(key) && data[key] !== null && data[key] !== undefined;
              }).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Additional Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(data || {})
                      .filter(([key]) => {
                        const displayedFields = [
                          'name', 'first_name', 'last_name', 'email', 'employee_number', 'status',
                          'department', 'position', 'employment_type', 'hire_date',
                          'base_salary', 'salary_currency', 'date_of_birth', 'mobile_phone',
                          'bank_account_number', 'bank_account_holder', 'bank_name',
                          'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
                        ];
                        return !displayedFields.includes(key) && data[key] !== null && data[key] !== undefined;
                      })
                      .map(([key, value]) => (
                        <div key={key} className="flex items-start justify-between gap-4">
                          <span className="text-sm text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
                          <span className="text-sm font-medium text-right max-w-xs break-words">
                            {typeof value === 'boolean' ? (value ? '✓' : '✗') : String(value)}
                          </span>
                        </div>
                      ))}
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        {detailConfig?.sidebar && !editMode && (
          <div className="space-y-4">
            {/* Workflow status */}
            {workflow && workflowState && (
              <Card>
                <CardHeader>
                  <CardTitle>Status</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-xs text-muted-foreground mb-2">Current State</p>
                    <Badge variant="default" className="text-base py-2 px-3">
                      {workflow.states[workflowState]?.label || workflowState}
                    </Badge>
                  </div>

                  {/* Available transitions */}
                  {onWorkflowTransition && (
                    <div className="space-y-2">
                      <p className="text-xs text-muted-foreground">Actions</p>
                      <div className="space-y-2">
                        {workflow.states[workflowState]?.can_transition_to.map((toState) => {
                          const transitionKey = Object.entries(workflow.transitions || {}).find(
                            ([_, t]) => t.from === workflowState && t.to === toState
                          )?.[0];

                          if (!transitionKey) return null;

                          const transition = (workflow.transitions || {})[transitionKey];

                          return (
                            <Button
                              key={transitionKey}
                              onClick={() => onWorkflowTransition(transitionKey)}
                              variant="outline"
                              size="sm"
                              className="w-full justify-start"
                            >
                              {transition.label}
                            </Button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Metadata */}
            {detailConfig?.sidebar?.show_metadata && (
              <Card>
                <CardHeader>
                  <CardTitle>Metadata</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  {data?.created_at && (
                    <div>
                      <p className="text-xs text-muted-foreground">Created</p>
                      <p>{new Date(data.created_at).toLocaleString()}</p>
                    </div>
                  )}
                  {data?.updated_at && (
                    <div>
                      <p className="text-xs text-muted-foreground">Updated</p>
                      <p>{new Date(data.updated_at).toLocaleString()}</p>
                    </div>
                  )}
                  {data?.created_by && (
                    <div>
                      <p className="text-xs text-muted-foreground">Created by</p>
                      <p>{data.created_by}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Related records */}
            {detailConfig?.related_records && detailConfig.related_records.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Related Records</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {detailConfig.related_records.map((rel, idx) => (
                    <div key={idx} className="text-sm">
                      <p className="font-medium">{rel.label}</p>
                      <p className="text-xs text-muted-foreground">
                        Endpoint: {rel.endpoint}
                      </p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>

      {/* Delete confirmation */}
      <AlertDialog open={deleteConfirm} onOpenChange={setDeleteConfirm}>
        <AlertDialogContent>
          <AlertDialogTitle>Delete Record?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. The record will be permanently deleted.
          </AlertDialogDescription>
          <div className="flex gap-2 justify-end">
            <AlertDialogCancel disabled={deleteLoading || isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleteLoading || isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteLoading || isDeleting ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </div>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
