from .Server import *
from ..utility import HealthCheck, SES

class AnimeWorld_Server(Server):
    def _token(self) -> str:
        """Token episodio: ultimo segmento dell'URL pagina episodio."""
        return self.link.rstrip("/").split("/")[-1]

    @HealthCheck
    def fileLink(self) -> str:
        """
        Recupera il link diretto per il download del file dell'episodio.

        Chiama il nuovo endpoint `/api/episode/info?id=<token>` (introdotto da
        AnimeWorld nel 2026 in sostituzione del deprecato `/api/download/<id>`)
        e ritorna il campo `grabber` della risposta JSON, ossia l'URL diretto
        al file MP4 servito dal CDN.

        Returns:
          Link diretto al file MP4.

        Example:
          ```py
          return str # Link del file
          ```
        """
        token = self._token()
        r = SES.get(
            "/api/episode/info",
            params={"id": token, "alt": 0},
            headers={
                "Referer": self.link,
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01",
            },
            follow_redirects=True,
        )
        r.raise_for_status()
        return r.json()["grabber"]

    def fileInfo(self) -> Dict[str,str]:
        """
        Recupera le informazioni del file dell'episodio.

        Returns:
          Informazioni file episodio.

        Example:
          ```py
          return {
            "content_type": str, # Tipo del file, es. video/mp4
            "total_bytes": int, # Byte totali del file
            "last_modified": datetime, # Data e ora dell'ultimo aggiornamento effettuato all'episodio sul server
            "server_name": str, # Nome del server
            "server_id": int, # ID del server
            "url": str # url dell'episodio
          }
          ```
        """

        return self._fileInfoIn()

    def download(self, title: Optional[str]=None, folder: Union[str, io.IOBase]='', *, hook: Callable[[Dict], None]=lambda *args:None, opt: List[str]=[]) -> Optional[str]:
        """
        Scarica l'episodio.

        Args:
          title: Nome con cui verrà nominato il file scaricato.
          folder: Posizione in cui verrà spostato il file scaricato.

        Other parameters:
          hook: Funzione che viene richiamata varie volte durante il download; la funzione riceve come argomento un dizionario con le seguenti chiavi:\n
            - `total_bytes`: Byte totali da scaricare.
            - `downloaded_bytes`: Byte attualmente scaricati.
            - `percentage`: Percentuale del progresso di download.
            - `speed`: Velocità di download (byte/s)
            - `elapsed`: Tempo trascorso dall'inizio del download.
            - `eta`: Tempo stimato rimanente per fine del download.
            - `status`: 'downloading' | 'finished' | 'aborted'
            - `filename`: Nome del file in download.

          opt: Lista per delle opzioni aggiuntive.\n
            - `'abort'`: Ferma forzatamente il download.

        Returns:
          Nome del file scaricato.

        Raises:
          HardStoppedDownload: Il file in download è stato forzatamente interrotto.

        Example:
          ```py
          return str # File scaricato
          ```
        """
        if title is None: title = self._defTitle
        else: title = self._sanitize(title)
        return self._downloadIn(title,folder,hook=hook,opt=opt)
