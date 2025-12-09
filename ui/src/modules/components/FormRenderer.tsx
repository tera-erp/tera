import React, { useState, useEffect, useRef } from 'react';
import { FormConfig, FormFieldConfig, FieldType } from '../types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { ChevronDown, AlertCircle, CheckCircle2, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface FormRendererProps {
  config: FormConfig;
  initialData?: Record<string, any>;
  onSubmit: (data: Record<string, any>) => Promise<void>;
  onCancel?: () => void;
  loading?: boolean;
  readOnly?: boolean;
  isEditing?: boolean;
  workflowState?: string;
}

interface FormErrors {
  [key: string]: string;
}

export const FormRenderer: React.FC<FormRendererProps> = ({
  config,
  initialData = {},
  onSubmit,
  onCancel,
  loading = false,
  readOnly = false,
  isEditing = false,
  workflowState,
}) => {
  // Use edit-specific title/description if in edit mode and available
  const displayTitle = isEditing && config.edit_title ? config.edit_title : config.title;
  const displayDescription = isEditing && config.edit_description ? config.edit_description : config.description;
  const displaySubmitLabel = isEditing && config.edit_submit_label ? config.edit_submit_label : config.submit_label;
  const [formData, setFormData] = useState<Record<string, any>>(initialData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitError, setSubmitError] = useState<string>('');
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [remoteOptions, setRemoteOptions] = useState<Record<string, { value: string; label: string }[]>>({});
  const navigate = useNavigate();
  const prevInitialDataRef = useRef<Record<string, any>>(initialData);

  // Only reset form when we have a meaningful ID change (switching between records)
  // For create mode or same record, preserve user input even on errors
  useEffect(() => {
    const prevId = prevInitialDataRef.current?.id;
    const newId = initialData?.id;
    
    // If ID changed, we're switching records - reset the form
    if (prevId !== newId) {
      setFormData(initialData);
      setErrors({});
      setSubmitError('');
      prevInitialDataRef.current = initialData;
    }
  }, [initialData?.id]);

  // Fetch remote options for select fields that declare an endpoint
  useEffect(() => {
    const fetchOptions = async () => {
      const entries = Object.entries(config.fields).filter(([, field]) => field.type === 'select' && field.endpoint);
      if (entries.length === 0) return;

      const optionsMap: Record<string, { value: string; label: string }[]> = {};
      await Promise.all(
        entries.map(async ([key, field]) => {
          try {
            const response = await fetch(field.endpoint as string);
            const data = await response.json();
            if (Array.isArray(data)) {
              const valField = field.value_field || 'id';
              const labelField = field.display_field || 'name';
              optionsMap[key] = data.map((item: any) => ({
                value: String(item[valField]),
                label: String(item[labelField] ?? item[valField]),
              }));
            }
          } catch (err) {
            console.warn(`Failed to load options for ${key} from ${field.endpoint}`, err);
          }
        })
      );
      if (Object.keys(optionsMap).length > 0) {
        setRemoteOptions(optionsMap);
      }
    };

    fetchOptions();
  }, [config]);

  const evaluateCondition = (expression: string, data: Record<string, any>): boolean => {
    try {
      // Create a safe evaluation context
      const context = new Function('data', `return ${expression}`);
      return context(data);
    } catch {
      console.warn(`Failed to evaluate condition: ${expression}`);
      return false;
    }
  };

  const evaluateFormula = (expression: string, data: Record<string, any>): any => {
    try {
      const context = new Function('data', `return ${expression}`);
      return context(data);
    } catch {
      console.warn(`Failed to evaluate formula: ${expression}`);
      return null;
    }
  };

  const formatReadOnlyValue = (value: any, field: FormFieldConfig): string => {
    if (value === null || value === undefined || value === '') {
      return '-';
    }

    switch (field.type) {
      case 'checkbox':
        return value ? 'Yes' : 'No';
      case 'date':
        if (typeof value === 'string') {
          return new Date(value).toLocaleDateString();
        }
        return value.toLocaleDateString();
      case 'datetime':
        if (typeof value === 'string') {
          return new Date(value).toLocaleString();
        }
        return value.toLocaleString();
      case 'number':
      case 'decimal':
        return typeof value === 'number' ? value.toLocaleString() : String(value);
      case 'select':
        // If options are available, find and return the label
        if (field.options) {
          const option = field.options.find(opt => opt.value === value);
          return option ? option.label : String(value);
        }
        return String(value);
      default:
        return String(value);
    }
  };

  const renderReadOnlyField = (key: string, field: FormFieldConfig) => {
    if (field.hidden || (field.hidden_if && evaluateCondition(field.hidden_if, formData))) {
      return null;
    }

    let value = formData[key];

    // Apply formulas for computed fields
    if (field.formula) {
      value = evaluateFormula(field.formula, formData);
    }

    const displayValue = formatReadOnlyValue(value, field);

    return (
      <div key={key} className="space-y-1">
        <Label htmlFor={key} className="text-sm font-medium">{field.label}</Label>
        <div className="flex items-center p-2.5 bg-slate-50 border border-slate-200 rounded-md text-slate-700 min-h-10">
          {displayValue}
        </div>
        {field.help_text && (
          <p className="text-xs text-muted-foreground">{field.help_text}</p>
        )}
      </div>
    );
  };

  const validateField = (key: string, value: any, field: FormFieldConfig): string | null => {
    if (field.required && (value === '' || value === null || value === undefined)) {
      return `${field.label} is required`;
    }

    if (field.minLength && typeof value === 'string' && value.length < field.minLength) {
      return `${field.label} must be at least ${field.minLength} characters`;
    }

    if (field.maxLength && typeof value === 'string' && value.length > field.maxLength) {
      return `${field.label} must be at most ${field.maxLength} characters`;
    }

    if (field.min !== undefined && typeof value === 'number' && value < Number(field.min)) {
      return `${field.label} must be at least ${field.min}`;
    }

    if (field.max !== undefined && typeof value === 'number' && value > Number(field.max)) {
      return `${field.label} must be at most ${field.max}`;
    }

    if (field.pattern && typeof value === 'string') {
      const regex = new RegExp(field.pattern);
      if (!regex.test(value)) {
        return `${field.label} format is invalid`;
      }
    }

    return null;
  };

  const handleFieldChange = (key: string, value: any) => {
    const newData = { ...formData, [key]: value };
    setFormData(newData);
    
    // Clear error for this field
    if (errors[key]) {
      setErrors({ ...errors, [key]: '' });
    }

    // Re-evaluate formulas that depend on this field
    Object.entries(config.fields).forEach(([fieldKey, fieldConfig]) => {
      if (fieldConfig.formula) {
        newData[fieldKey] = evaluateFormula(fieldConfig.formula, newData);
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError('');
    setSubmitSuccess(false);

    // Validate all fields
    const newErrors: FormErrors = {};
    Object.entries(config.fields).forEach(([key, field]) => {
      // Skip validation for readonly/disabled fields
      if (field.readonly || field.disabled) {
        return;
      }
      const error = validateField(key, formData[key], field);
      if (error) {
        newErrors[key] = error;
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      await onSubmit(formData);
      setSubmitSuccess(true);
      // Auto-clear success message after 3 seconds
      setTimeout(() => {
        setSubmitSuccess(false);
      }, 3000);
    } catch (error) {
      let errorMessage = 'Failed to submit form';
      
      // Try to extract detailed error message from the error object
      if (error instanceof Error) {
        errorMessage = error.message;
        
        // Try to parse JSON error response if available
        try {
          const errorData = JSON.parse(error.message);
          if (errorData.detail) {
            if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
              // Handle validation errors from FastAPI/Pydantic
              errorMessage = errorData.detail
                .map((err: any) => {
                  if (typeof err === 'string') return err;
                  if (err.msg) {
                    const field = err.loc?.[err.loc.length - 1] || 'Field';
                    return `${field}: ${err.msg}`;
                  }
                  return JSON.stringify(err);
                })
                .join('; ');
            }
          }
        } catch {
          // Not JSON, use the error message as-is
        }
      }
      
      setSubmitError(errorMessage);
    }
  };

  const handleBackClick = () => {
    if (config.back_button?.navigate_to) {
      navigate(config.back_button.navigate_to);
    } else if (onCancel) {
      onCancel();
    } else {
      navigate(-1);
    }
  };

  const renderField = (key: string, field: FormFieldConfig) => {
    // Check visibility conditions
    if (field.hidden || (field.hidden_if && evaluateCondition(field.hidden_if, formData))) {
      return null;
    }

    // Render readonly fields as display values
    if (field.readonly || field.disabled) {
      return renderReadOnlyField(key, field);
    }

    // If workflow state makes this field readonly, render as readonly
    const isWorkflowReadonly = workflowState && field.disabled_if?.includes?.(workflowState);

    const isDisabled = readOnly ||
      isWorkflowReadonly ||
      (field.disabled_if && evaluateCondition(field.disabled_if, formData)) ||
      loading;

    let value = formData[key];
    
    // Apply formulas for computed fields
    if (field.formula) {
      value = evaluateFormula(field.formula, formData);
    }

    const error = errors[key];

    const inputProps = {
      value: value ?? '',
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
        handleFieldChange(key, e.target.value),
      disabled: isDisabled,
      className: error ? 'border-destructive' : '',
    };

    let fieldContent;

    switch (field.type) {
      case 'text':
      case 'email':
        fieldContent = (
          <Input
            {...inputProps}
            type={field.type}
            placeholder={field.placeholder}
          />
        );
        break;

      case 'number':
      case 'decimal':
        fieldContent = (
          <Input
            {...inputProps}
            type="number"
            step={field.type === 'decimal' ? '0.01' : '1'}
            placeholder={field.placeholder}
          />
        );
        break;

      case 'date':
      case 'datetime':
        fieldContent = (
          <Input
            {...inputProps}
            type={field.type === 'datetime' ? 'datetime-local' : 'date'}
          />
        );
        break;

      case 'textarea':
      case 'richtext':
        fieldContent = (
          <Textarea
            {...(inputProps as any)}
            placeholder={field.placeholder}
            rows={4}
          />
        );
        break;

      case 'select':
        const selectOptions = (field.options && field.options.length > 0)
          ? field.options
          : remoteOptions[key] || [];
        fieldContent = (
          <Select
            value={value?.toString() || ''}
            onValueChange={(val) => handleFieldChange(key, val)}
            disabled={isDisabled}
          >
            <SelectTrigger>
              <SelectValue placeholder={field.placeholder || 'Select an option'} />
            </SelectTrigger>
            <SelectContent>
              {selectOptions.length > 0 ? (
                selectOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))
              ) : field.endpoint ? (
                <div className="px-2 py-1.5 text-sm text-muted-foreground">
                  Loading options from {field.endpoint}...
                </div>
              ) : (
                <div className="px-2 py-1.5 text-sm text-muted-foreground">
                  No options available
                </div>
              )}
            </SelectContent>
          </Select>
        );
        break;

      case 'checkbox':
        fieldContent = (
          <div className="flex items-center gap-2">
            <Checkbox
              checked={value || false}
              onCheckedChange={(checked) => handleFieldChange(key, checked)}
              disabled={isDisabled}
            />
            <Label htmlFor={key} className="font-normal">
              {field.label}
            </Label>
          </div>
        );
        break;

      case 'array':
        fieldContent = (
          <div className="space-y-2 border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">
              Array field: {field.fields ? Object.keys(field.fields).join(', ') : 'no sub-fields'}
            </p>
            {/* TODO: Implement array/nested form rendering */}
          </div>
        );
        break;

      default:
        fieldContent = <div className="text-red-500">Unsupported field type: {field.type}</div>;
    }

    if (field.type === 'checkbox') {
      return (
        <div key={key} className="space-y-1">
          {fieldContent}
          {field.help_text && (
            <p className="text-xs text-muted-foreground">{field.help_text}</p>
          )}
          {error && (
            <p className="text-xs text-destructive flex items-center gap-1">
              <AlertCircle className="h-3 w-3" /> {error}
            </p>
          )}
        </div>
      );
    }

    return (
      <div key={key} className="space-y-1">
        <Label htmlFor={key}>{field.label}{field.required ? ' *' : ''}</Label>
        {fieldContent}
        {field.help_text && (
          <p className="text-xs text-muted-foreground">{field.help_text}</p>
        )}
        {error && (
          <p className="text-xs text-destructive flex items-center gap-1">
            <AlertCircle className="h-3 w-3" /> {error}
          </p>
        )}
      </div>
    );
  };

  const renderByLayout = () => {
    const layout = config.layout;

    if (!layout || layout.type === 'grid') {
      const cols = layout?.columns || 2;
      const fields = Object.entries(config.fields);

      return (
        <div className={`grid grid-cols-${cols} gap-${layout?.gaps === 'large' ? '6' : layout?.gaps === 'small' ? '2' : '4'}`}>
          {fields.map(([key, field]) => renderField(key, field))}
        </div>
      );
    }

    if (layout.type === 'tabs' && layout.sections) {
      return (
        <Tabs defaultValue={layout.sections[0]?.title || '0'} className="w-full">
          <TabsList className="grid w-full" style={{ gridTemplateColumns: `repeat(${layout.sections.length}, 1fr)` }}>
            {layout.sections.map((section, idx) => (
              <TabsTrigger key={idx} value={section.title || idx.toString()}>
                {section.title || `Tab ${idx + 1}`}
              </TabsTrigger>
            ))}
          </TabsList>
          {layout.sections.map((section, idx) => (
            <TabsContent key={idx} value={section.title || idx.toString()} className="space-y-4">
              {section.description && (
                <p className="text-sm text-muted-foreground">{section.description}</p>
              )}
              <div className="grid grid-cols-2 gap-4">
                {section.fields.map((fieldKey) =>
                  config.fields[fieldKey] ? renderField(fieldKey, config.fields[fieldKey]) : null
                )}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      );
    }

    if (layout.type === 'accordion' && layout.sections) {
      return (
        <div className="space-y-2">
          {layout.sections.map((section, idx) => (
            <Collapsible key={idx} defaultOpen={idx === 0}>
              <CollapsibleTrigger className="flex items-center gap-2 font-semibold hover:opacity-75">
                <ChevronDown className="h-4 w-4" />
                {section.title || `Section ${idx + 1}`}
              </CollapsibleTrigger>
              <CollapsibleContent className="space-y-4 pt-4">
                {section.description && (
                  <p className="text-sm text-muted-foreground">{section.description}</p>
                )}
                <div className="grid grid-cols-2 gap-4">
                  {section.fields.map((fieldKey) =>
                    config.fields[fieldKey] ? renderField(fieldKey, config.fields[fieldKey]) : null
                  )}
                </div>
              </CollapsibleContent>
            </Collapsible>
          ))}
        </div>
      );
    }

    // Default layout
    return (
      <div className="grid grid-cols-2 gap-4">
        {Object.entries(config.fields).map(([key, field]) => renderField(key, field))}
      </div>
    );
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center gap-3">
          {config.back_button?.enabled && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleBackClick}
              className="p-0 h-auto flex-shrink-0"
              title={config.back_button.label || 'Back'}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
          )}
          <div className="flex-1 min-w-0">
            <CardTitle>{displayTitle}</CardTitle>
            {displayDescription && <CardDescription>{displayDescription}</CardDescription>}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {submitError && (
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 flex gap-3">
              <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-destructive font-medium">Error</p>
                <p className="text-sm text-destructive/90 break-words">{submitError}</p>
              </div>
            </div>
          )}

          {submitSuccess && (
            <div className="rounded-lg bg-green-50 border border-green-200 p-4 flex gap-3">
              <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-green-700 font-medium">Success</p>
                <p className="text-sm text-green-600">Your record has been saved successfully</p>
              </div>
            </div>
          )}

          {renderByLayout()}

          <div className="flex gap-2 justify-end">
            {onCancel ? (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={loading}
              >
                {config.cancel_label || 'Cancel'}
              </Button>
            ) : null}
            {!readOnly && (
              <Button
                type="submit"
                disabled={loading}
              >
                {loading ? 'Submitting...' : (displaySubmitLabel || 'Save')}
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
};
