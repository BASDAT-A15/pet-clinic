from django import forms

class TreatmentForm(forms.Form):
    # Pilihan ID Kunjungan
    ID_Kunjungan = forms.ChoiceField(
        choices=[('KJN001', 'KJN001'), ('KJN002', 'KJN002'), ('KJN003', 'KJN003')],
        label="Kunjungan"
    )
    
    # Pilihan Jenis Perawatan
    jenis_perawatan = forms.ChoiceField(
        choices=[('TRM001', 'TRM001 - Dental Care'), ('TRM002', 'TRM002 - Parasite Control'), ('TRM003', 'TRM003 - Flea Treatment')],
        label="Jenis Perawatan"
    )
    
    # Catatan Medis
    catatan_medis = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Catatan Medis...'}),
        required=False,
        label="Catatan Medis"
    )
