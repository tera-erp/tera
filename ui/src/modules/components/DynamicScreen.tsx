import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ModuleFactory } from '@/modules';
import { FormRenderer, ListRenderer, DetailRenderer } from '@/modules/components';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { AlertCircle, Loader2 } from 'lucide-react';

interface DynamicScreenProps {
  moduleId: string;
  screenId: string;
}

export const DynamicScreen: React.FC<DynamicScreenProps> = ({ moduleId, screenId }) => {
  const navigate = useNavigate();
  const { id: recordId } = useParams<{ id?: string }>();
  const [editMode, setEditMode] = useState(false);

  // Get module config
  const moduleConfig = ModuleFactory.getModule(moduleId);
  const screenConfig = moduleConfig?.screens?.[screenId];

  if (!moduleConfig || !screenConfig) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 flex gap-3">
            <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
            <p className="text-sm text-destructive">Screen not found</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Check if this is a new record creation
  const isCreating = recordId === 'new';

  // Fetch list data if list type
  const {
    data: listData = [],
    isLoading: listLoading,
    error: listError,
  } = useQuery(
    [moduleId, screenId, 'list'],
    async () => {
      if (screenConfig.type !== 'list' || !screenConfig.endpoint) return [];
      const response = await fetch(screenConfig.endpoint, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch list');
      return response.json();
    },
    {
      enabled: screenConfig.type === 'list',
    }
  );

  // Fetch detail data if detail type (but not for new records)
  const {
    data: detailData,
    isLoading: detailLoading,
    error: detailError,
  } = useQuery(
    [moduleId, screenId, recordId],
    async () => {
      if (screenConfig.type !== 'detail' || !recordId || isCreating || !screenConfig.endpoint) {
        return null;
      }
      const endpoint = screenConfig.endpoint.replace('{id}', recordId);
      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch record');
      return response.json();
    },
    {
      enabled: screenConfig.type === 'detail' && !!recordId && !isCreating,
    }
  );

  // Helper to resolve screen paths
  const resolvePath = (targetScreenId: string, id?: string) => {
    const target = moduleConfig?.screens?.[targetScreenId];
    if (!target?.path) return `/modules/${moduleId}`;
    return id ? target.path.replace('{id}', id) : target.path;
  };

  // Edit/Create mutation
  const editMutation = useMutation({
    mutationFn: async (data: any) => {
      if (isCreating) {
        // Creating new record
        if (!screenConfig.endpoint) throw new Error('No endpoint');
        const response = await fetch(screenConfig.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify(data),
        });
        
        if (!response.ok) {
          // Try to extract error message from response
          try {
            const errorData = await response.json();
            const errorMessage = errorData.detail || JSON.stringify(errorData);
            throw new Error(errorMessage);
          } catch (e) {
            if (e instanceof Error && e.message !== 'Failed to create record') {
              throw e;
            }
            throw new Error(`Failed to create record (${response.status} ${response.statusText})`);
          }
        }
        return response.json();
      } else {
        // Updating existing record
        if (!recordId || !screenConfig.endpoint) throw new Error('No endpoint');
        const endpoint = screenConfig.endpoint.replace('{id}', recordId);
        const response = await fetch(endpoint, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify(data),
        });
        
        if (!response.ok) {
          // Try to extract error message from response
          try {
            const errorData = await response.json();
            const errorMessage = errorData.detail || JSON.stringify(errorData);
            throw new Error(errorMessage);
          } catch (e) {
            if (e instanceof Error && e.message !== 'Failed to update record') {
              throw e;
            }
            throw new Error(`Failed to update record (${response.status} ${response.statusText})`);
          }
        }
        return response.json();
      }
    },
    onSuccess: (response) => {
      setEditMode(false);
      if (isCreating) {
        // Navigate to the created record using declarative path
        navigate(resolvePath(screenId, String(response.id)));
      }
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!recordId || !screenConfig.endpoint) throw new Error('No endpoint');
      const endpoint = screenConfig.endpoint.replace('{id}', recordId);
      const response = await fetch(endpoint, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to delete record');
      return response.json();
    },
    onSuccess: () => {
      navigate(resolvePath(screenId));
    },
  });

  // Render based on screen type
  switch (screenConfig.type) {
    case 'list':
      return (
        <ListRenderer
          config={screenConfig}
          data={listData}
          loading={listLoading}
          error={listError instanceof Error ? listError.message : undefined}
          onNew={() => {
            const createTargetId = screenConfig.create_screen || screenId;
            const targetPath = resolvePath(createTargetId, 'new');
            navigate(targetPath);
          }}
          onRow={(record) => navigate(resolvePath(screenId, String(record.id)))}
        />
      );

    case 'detail':
      return (
        <DetailRenderer
          config={screenConfig}
          formConfig={
            screenConfig.detail_config?.form
              ? moduleConfig?.forms?.[screenConfig.detail_config.form]
              : undefined
          }
          recordId={recordId || 'new'}
          data={detailData}
          loading={detailLoading && !isCreating}
          error={detailError instanceof Error ? detailError.message : undefined}
          isCreating={isCreating}
          onBack={() => navigate(resolvePath(screenId))}
          onEdit={editMutation.mutate}
          onDelete={deleteMutation.mutate}
          editMode={editMode}
          onEditModeChange={setEditMode}
        />
      );

    case 'form':
      return (
        <FormRenderer
          config={screenConfig as any}
          initialData={detailData}
          onSubmit={editMutation.mutate}
          onCancel={() => navigate(resolvePath(screenId))}
          loading={editMutation.isPending}
          readOnly={false}
        />
      );

    default:
      return (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">
              Screen type '{screenConfig.type}' not supported
            </p>
          </CardContent>
        </Card>
      );
  }
};
