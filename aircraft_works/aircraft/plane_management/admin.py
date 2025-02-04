from django.contrib.admin import register, ModelAdmin

from aircraft.plane_management.models import Part, PartUsage, PlaneAssembly

@register(Part)
class PartAdmin(ModelAdmin):
    list_display = ["id", "part_type", "plane_type", "user", "used_in_plane"]
    list_filter = ["part_type", "user", "plane_type", "used_in_plane"]
    search_fields = ["part_type", "user", "plane_type"]
    ordering = ["-id"]
    readonly_fields = ["created_at", "updated_at"]
    def save_model(self, request, obj, form, change):
        obj.clean()
        super().save_model(request, obj, form, change)


@register(PartUsage)
class PartUsageAdmin(ModelAdmin):
    list_display = ["id", "part", "plane_assembly"]
    list_filter = ["part"]
    search_fields = ["part"]
    ordering = ["-id"]
    readonly_fields = ["created_at", "updated_at"]


@register(PlaneAssembly)
class PlaneAssemblyAdmin(ModelAdmin):
    list_display = ["id", "plane_type", "user", "list_parts_used"]
    list_filter = ["plane_type", "user"]
    search_fields = ["plane_type", "user"]
    ordering = ["-id"]
    readonly_fields = ["created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        obj.clean()
        super().save_model(request, obj, form, change)

    def list_parts_used(self, obj):
        return ", ".join([part.part_type for part in obj.parts_used.all()])
    list_parts_used.short_description = "Parts Used"