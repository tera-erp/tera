import React, { useState, useEffect } from 'react';
import { ScreenConfig } from '../types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { AlertCircle, Loader2, Plus, Search, MoreHorizontal, ChevronLeft, ChevronRight } from 'lucide-react';
import * as LucideIcons from 'lucide-react';
import apiClient from '@/lib/api-client';
import { toast } from 'sonner';

interface ListRendererProps {
  config: ScreenConfig;
  data: any[];
  loading?: boolean;
  error?: string;
  onNew?: () => void;
  onRow?: (record: any) => void;
  onAction?: (actionId: string, record: any) => Promise<void>;
  totalRecords?: number;
  currentPage?: number;
  onPageChange?: (page: number) => void;
}

export const ListRenderer: React.FC<ListRendererProps> = ({
  config,
  data = [],
  loading = false,
  error,
  onNew,
  onRow,
  onAction,
  totalRecords = data.length,
  currentPage = 1,
  onPageChange,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const listConfig = config.list_config;

  if (!listConfig) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground">List configuration not available</p>
        </CardContent>
      </Card>
    );
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedRows(new Set(data.map((r, idx) => `row-${idx}`)));
    } else {
      setSelectedRows(new Set());
    }
  };

  const handleSelectRow = (rowId: string, checked: boolean) => {
    const newSelected = new Set(selectedRows);
    if (checked) {
      newSelected.add(rowId);
    } else {
      newSelected.delete(rowId);
    }
    setSelectedRows(newSelected);
  };

  const getIconComponent = (iconName: string | undefined) => {
    if (!iconName) return null;
    const Icon = (LucideIcons as any)[iconName];
    return Icon ? <Icon className="h-4 w-4" /> : null;
  };

  const filteredData = searchTerm
    ? data.filter((row) => {
        const searchFields = listConfig.searchable_fields || listConfig.columns;
        return searchFields.some((field) =>
          String(row[field]).toLowerCase().includes(searchTerm.toLowerCase())
        );
      })
    : data;

  const sortedData = sortBy
    ? [...filteredData].sort((a, b) => {
        const aVal = a[sortBy];
        const bVal = b[sortBy];
        const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        return sortOrder === 'asc' ? comparison : -comparison;
      })
    : filteredData;

  const pageSize = listConfig.page_size || 25;
  const totalPages = Math.ceil(totalRecords / pageSize);

  const handlePrint = async (action: any, record: any) => {
    const endpointTemplate = action.print_endpoint || action.endpoint;
    if (!endpointTemplate) {
      toast.error('No print endpoint configured');
      return;
    }

    const formatList: string[] = action.print_formats || ['pdf'];
    const format = (formatList[0] || 'pdf').toLowerCase();

    const resolveTemplate = (template: string) => {
      // Replace {id} placeholders with record.id if available
      return template.replace('{id}', record.id ?? record.uuid ?? record.invoice_id ?? '');
    };

    const url = resolveTemplate(endpointTemplate) + (endpointTemplate.includes('?') ? '' : `?format=${format}`);

    try {
      const response = await apiClient.get(url, { responseType: 'blob' });
      const blob = response.data;
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      const ext = format;
      const baseName = record.invoice_number || record.payslip_number || record.name || record.id || 'document';
      link.href = downloadUrl;
      link.download = `${baseName}.${ext}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      toast.success(`Downloaded ${baseName}.${ext}`);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'Failed to download document';
      toast.error(detail);
    }
  };

  const renderCell = (record: any, fieldKey: string) => {
    const value = record[fieldKey];

    if (value === null || value === undefined) {
      return <span className="text-muted-foreground">—</span>;
    }

    if (typeof value === 'boolean') {
      return <span>{value ? '✓' : '✗'}</span>;
    }

    if (typeof value === 'object') {
      return <span className="text-muted-foreground">[Object]</span>;
    }

    if (typeof value === 'number') {
      return <span className="text-right font-mono">{value.toLocaleString()}</span>;
    }

    return <span>{String(value).substring(0, 100)}</span>;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle>{config.title}</CardTitle>
            {config.description && <CardDescription>{config.description}</CardDescription>}
          </div>
          {onNew && (
            <Button onClick={onNew} className="gap-2">
              <Plus className="h-4 w-4" />
              New
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Toolbar */}
        <div className="flex gap-2 items-center flex-wrap">
          {listConfig.searchable_fields && listConfig.searchable_fields.length > 0 && (
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
          )}

          {listConfig.sortable && (
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Sort by..." />
              </SelectTrigger>
              <SelectContent>
                {listConfig.columns.map((col) => (
                  <SelectItem key={col} value={col}>
                    {col}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          {sortBy && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </Button>
          )}
        </div>

        {/* Error state */}
        {error && (
          <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 flex gap-3">
            <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="flex gap-2 items-center">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              <p className="text-muted-foreground">Loading...</p>
            </div>
          </div>
        ) : sortedData.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <p className="text-muted-foreground">No records found</p>
          </div>
        ) : (
          <div className="overflow-x-auto border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  {listConfig.selectable && (
                    <TableHead className="w-12">
                      <Checkbox
                        checked={selectedRows.size === data.length && data.length > 0}
                        onCheckedChange={handleSelectAll}
                      />
                    </TableHead>
                  )}
                  {listConfig.columns.map((col) => (
                    <TableHead
                      key={col}
                      className={listConfig.sortable ? 'cursor-pointer hover:bg-muted/50' : ''}
                      onClick={() => {
                        if (listConfig.sortable) {
                          setSortBy(col);
                          setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                        }
                      }}
                    >
                      {col}
                      {sortBy === col && <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>}
                    </TableHead>
                  ))}
                  {listConfig.row_actions && listConfig.row_actions.length > 0 && (
                    <TableHead className="w-12 text-right">Actions</TableHead>
                  )}
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedData.map((record, idx) => {
                  const rowId = `row-${idx}`;
                  return (
                    <TableRow
                      key={rowId}
                      className={onRow ? 'cursor-pointer hover:bg-muted/50' : ''}
                      onClick={() => onRow && onRow(record)}
                    >
                      {listConfig.selectable && (
                        <TableCell onClick={(e) => e.stopPropagation()}>
                          <Checkbox
                            checked={selectedRows.has(rowId)}
                            onCheckedChange={(checked) => handleSelectRow(rowId, checked as boolean)}
                          />
                        </TableCell>
                      )}
                      {listConfig.columns.map((col) => (
                        <TableCell key={col}>{renderCell(record, col)}</TableCell>
                      ))}
                      {listConfig.row_actions && listConfig.row_actions.length > 0 && (
                        <TableCell onClick={(e) => e.stopPropagation()} className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              {listConfig.row_actions.map((action) => (
                                <DropdownMenuItem
                                  key={action.id}
                                  onClick={async () => {
                                    if (action.action === 'print') {
                                      await handlePrint(action, record);
                                    } else {
                                      await onAction?.(action.id, record);
                                    }
                                  }}
                                >
                                  {getIconComponent(action.icon)}
                                  <span className="ml-2">{action.label}</span>
                                </DropdownMenuItem>
                              ))}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      )}
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}

        {/* Pagination */}
        {listConfig.paginated && totalPages > 1 && (
          <div className="flex items-center justify-between pt-4">
            <p className="text-sm text-muted-foreground">
              Showing page {currentPage} of {totalPages} ({totalRecords} total records)
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange?.(currentPage - 1)}
                disabled={currentPage <= 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange?.(currentPage + 1)}
                disabled={currentPage >= totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
