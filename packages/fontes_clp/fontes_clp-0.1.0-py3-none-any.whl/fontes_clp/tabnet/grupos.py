from enum import Enum

_nomes_grupos_obitos = {
    1: "Pedestre traumatizado em um acidente de transporte",
    2: "Ciclista traumatizado em um acidente de transporte",
    3: "Motociclista traumat em um acidente de transporte",
    4: "Ocupante triciclo motorizado traumat acid transp",
    5: "Ocupante automóvel traumat acidente transporte",
    6: "Ocupante caminhonete traumat acidente transporte",
    7: "Ocupante veíc transp pesado traumat acid transp",
    8: "Ocupante ônibus traumat acidente de transporte",
    9: "Outros acidentes de transporte terrestre",
    10: "Acidentes de transporte por água",
    11: "Acidentes de transporte aéreo e espacial",
    12: "Outros acidentes de transporte e os não especif",
    13: "Quedas",
    14: "Exposição a forças mecânicas inanimadas",
    15: "Exposição a forças mecânicas animadas",
    16: "Afogamento e submersão acidentais",
    17: "Outros riscos acidentais à respiração",
    18: "Expos corr elétr, radiação e temp press extrem amb",
    19: "Exposição à fumaça, ao fogo e às chamas",
    20: "Contato com fonte de calor ou substâncias quentes",
    21: "Contato com animais e plantas venenosos",
    22: "Exposição às forças da natureza",
    23: "Envenenamento acidental e exposição subst nocivas",
    24: "Excesso de esforços, viagens e privações",
    25: "Exposição acidental a outr fatores e aos não espec",
    26: "Lesões autoprovocadas intencionalmente",
    27: "Agressões",
    28: "Eventos (fatos) cuja intenção é indeterminada",
    29: "Intervenções legais e operações de guerra",
    30: "Ef advers drog, medic e subst biológ finalid terap",
    31: "Acid ocorr pacientes prest cuid médicos e cirúrg",
    32: "Incid advers atos diagn terap assoc disposit médic",
    33: "Reaç anorm compl tard proc cirúrg méd s/menç acid",
    34: "Seqüelas causas externas de morbidade e mortalidad",
    35: "Fatores supl relac causas de morbid e mortalid COP",
}

_nomes_grupos_causas = {
    1: "V01-V09 Pedestre traumatizado acid transporte",
    2: "V10-V19 Ciclista traumatizado acid transporte",
    3: "V20-V29 Motociclista traumatizado acid transp",
    4: "V30-V39 Ocup triciclo motor traum acid transp",
    5: "V40-V49 Ocup automóvel traum acid transporte",
    6: "V50-V59 Ocup caminhonete traum acid transporte",
    7: "V60-V69 Ocup veíc transp pesado traum acid tran",
    8: "V70-V79 Ocup ônibus traumatizado acid transport",
    9: "V80-V89 Outros acid transporte terrestre",
    10: "V90-V94 Acidentes de transporte por água",
    11: "V95-V97 Acidentes de transporte aéreo/espacial",
    12: "V98-V99 Outros acid transporte e os não especif",
    13: "W00-W19 Quedas",
    14: "W20-W49 Exposição a forças mecânicas inanimadas",
    15: "W50-W64 Exposição a forças mecânicas animadas",
    16: "W65-W74 Afogamento e submersão acidentais",
    17: "W75-W84 Outros riscos acidentais à respiração",
    18: "W85-W99 Expos cor.elétr,rad.,temp pressão extr",
    19: "X00-X09 Exposição à fumaça, ao fogo e às chamas",
    20: "X10-X19 Contato fonte de calor e subst quentes",
    21: "X20-X29 Contato animais e plantas venenosos",
    22: "X30-X39 Exposição às forças da natureza",
    23: "X40-X49 Enven/intox acid expos a subst nocivas",
    24: "X50-X57 Excesso de esforços viagens e privações",
    25: "X58-X59 Expos acid a outr fatores e não espec",
    26: "X60-X84 Lesões autoprovocadas voluntariamente",
    27: "X85-Y09 Agressões",
    28: "Y10-Y34 Eventos cuja intenção é indeterminada",
    29: "Y35-Y36 Intervenções legais e operações de guerra",
    30: "Y40-Y84 Complic assistência médica e cirúrgica",
    31: "Y85-Y89 Seqüelas de causas externas",
    32: "Y90-Y98 Fatores suplement relac outras causas",
    33: "S-T Causas externas não classificadas",
}


class GruposObitos(Enum):
    # Agrupamentos
    ACIDENTES_TERRESTRES = range(1, 10)

    PEDESTRE_TRAUMATIZADO_EM_UM_ACIDENTE_DE_TRANSPORTE = 1
    CICLISTA_TRAUMATIZADO_EM_UM_ACIDENTE_DE_TRANSPORTE = 2
    MOTOCICLISTA_TRAUMAT_EM_UM_ACIDENTE_DE_TRANSPORTE = 3
    OCUPANTE_TRICICLO_MOTORIZADO_TRAUMAT_ACID_TRANSP = 4
    OCUPANTE_AUTOMOVEL_TRAUMAT_ACIDENTE_TRANSPORTE = 5
    OCUPANTE_CAMINHONETE_TRAUMAT_ACIDENTE_TRANSPORTE = 6
    OCUPANTE_VEIC_TRANSP_PESADO_TRAUMAT_ACID_TRANSP = 7
    OCUPANTE_ONIBUS_TRAUMAT_ACIDENTE_DE_TRANSPORTE = 8
    OUTROS_ACIDENTES_DE_TRANSPORTE_TERRESTRE = 9
    ACIDENTES_DE_TRANSPORTE_POR_AGUA = 10
    ACIDENTES_DE_TRANSPORTE_AEREO_E_ESPACIAL = 11
    OUTROS_ACIDENTES_DE_TRANSPORTE_E_OS_NAO_ESPECIF = 12
    QUEDAS = 13
    EXPOSICAO_A_FORCAS_MECANICAS_INANIMADAS = 14
    EXPOSICAO_A_FORCAS_MECANICAS_ANIMADAS = 15
    AFOGAMENTO_E_SUBMERSAO_ACIDENTAIS = 16
    OUTROS_RISCOS_ACIDENTAIS_A_RESPIRACAO = 17
    EXPOS_CORR_ELETR_RADIACAO_E_TEMP_PRESS_EXTREM_AMB = 18
    EXPOSICAO_A_FUMACA_AO_FOGO_E_AS_CHAMAS = 19
    CONTATO_COM_FONTE_DE_CALOR_OU_SUBSTANCIAS_QUENTES = 20
    CONTATO_COM_ANIMAIS_E_PLANTAS_VENENOSOS = 21
    EXPOSICAO_AS_FORCAS_DA_NATUREZA = 22
    ENVENENAMENTO_ACIDENTAL_E_EXPOSICAO_SUBST_NOCIVAS = 23
    EXCESSO_DE_ESFORCOS_VIAGENS_E_PRIVACOES = 24
    EXPOSICAO_ACIDENTAL_A_OUTR_FATORES_E_AOS_NAO_ESPEC = 25
    LESOES_AUTOPROVOCADAS_INTENCIONALMENTE = 26
    AGRESSOES = 27
    EVENTOS_FATOS_CUJA_INTENCAO_E_INDETERMINADA = 28
    INTERVENCOES_LEGAIS_E_OPERACOES_DE_GUERRA = 29
    EF_ADVERS_DROG_MEDIC_E_SUBST_BIOLOG_FINALID_TERAP = 30
    ACID_OCORR_PACIENTES_PREST_CUID_MEDICOS_E_CIRURG = 31
    INCID_ADVERS_ATOS_DIAGN_TERAP_ASSOC_DISPOSIT_MEDIC = 32
    REAC_ANORM_COMPL_TARD_PROC_CIRURG_MED_S_MENC_ACID = 33
    SEQUELAS_CAUSAS_EXTERNAS_DE_MORBIDADE_E_MORTALIDAD = 34
    FATORES_SUPL_RELAC_CAUSAS_DE_MORBID_E_MORTALID_COP = 35

    def get_nome(self) -> str:
        if self == self.ACIDENTES_TERRESTRES:
            return "Acidentes terrestres"

        return _nomes_grupos_obitos.get(self.value)

    def get_sigla(self) -> str:
        return self.name


class GruposCausas(Enum):
    # Agrupamentos
    ACIDENTES_TERRESTRES = range(1, 10)

    PEDESTRE_TRAUMATIZADO_ACID_TRANSPORTE = 1
    CICLISTA_TRAUMATIZADO_ACID_TRANSPORTE = 2
    MOTOCICLISTA_TRAUMATIZADO_ACID_TRANSP = 3
    OCUP_TRICICLO_MOTOR_TRAUM_ACID_TRANSP = 4
    OCUP_AUTOMOVEL_TRAUM_ACID_TRANSPORTE = 5
    OCUP_CAMINHONETE_TRAUM_ACID_TRANSPORTE = 6
    OCUP_VEIC_TRANSP_PESADO_TRAUM_ACID_TRAN = 7
    OCUP_ONIBUS_TRAUMATIZADO_ACID_TRANSPORT = 8
    OUTROS_ACID_TRANSPORTE_TERRESTRE = 9
    ACIDENTES_DE_TRANSPORTE_POR_AGUA = 10
    ACIDENTES_DE_TRANSPORTE_AEREO_ESPACIAL = 11
    OUTROS_ACID_TRANSPORTE_E_OS_NAO_ESPECIF = 12
    QUEDAS = 13
    EXPOSICAO_A_FORCAS_MECANICAS_INANIMADAS = 14
    EXPOSICAO_A_FORCAS_MECANICAS_ANIMADAS = 15
    AFOGAMENTO_E_SUBMERSAO_ACIDENTAIS = 16
    OUTROS_RISCOS_ACIDENTAIS_A_RESPIRACAO = 17
    EXPOS_COR_ELETR_RAD_TEMP_PRESSAO_EXTR = 18
    EXPOSICAO_A_FUMACA_AO_FOGO_E_AS_CHAMAS = 19
    CONTATO_FONTE_DE_CALOR_E_SUBST_QUENTES = 20
    CONTATO_ANIMAIS_E_PLANTAS_VENENOSOS = 21
    EXPOSICAO_AS_FORCAS_DA_NATUREZA = 22
    ENVEN_INTOX_ACID_EXPOS_A_SUBST_NOCIVAS = 23
    EXCESSO_DE_ESFORCOS_VIAGENS_E_PRIVACOES = 24
    EXPOS_ACID_A_OUTR_FATORES_E_NAO_ESPEC = 25
    LESOES_AUTOPROVOCADAS_VOLUNTARIAMENTE = 26
    AGRESSOES = 27
    EVENTOS_CUJA_INTENCAO_E_INDETERMINADA = 28
    INTERVENCOES_LEGAIS_E_OPERACOES_DE_GUERRA = 29
    COMPLIC_ASSISTENCIA_MEDICA_E_CIRURGICA = 30
    SEQUELAS_DE_CAUSAS_EXTERNAS = 31
    FATORES_SUPLEMENT_RELAC_OUTRAS_CAUSAS = 32
    CAUSAS_EXTERNAS_NAO_CLASSIFICADAS = 33

    def get_nome(self) -> str:
        if self == self.ACIDENTES_TERRESTRES:
            return "Acidentes terrestres"

        return _nomes_grupos_causas.get(self.value)

    def get_sigla(self) -> str:
        return self.name
