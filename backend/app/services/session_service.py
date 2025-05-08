# app/services/session_service.py
import shutil
from typing import List, Dict, Any, Optional
import os

from sqlalchemy.orm import Session as DBSession

from app.core.base import MethodExtractor, StructAlgorithm
from app.core.utils import load_class
from app.models.algorithm_registry import AlgorithmRegistry
from app.models.method_registry import MethodRegistry
from app.schemas.session_schemas import SessionCreate
from app.utils.file_analyzer import get_file_hash, get_file_size, get_file_type, get_mime_type

from ..models.struct_session import StructSession, SessionStatus
from ..models.file_instruction import FileInstruction, ActionType, InstructionStatus

from ..utils.directory_scanner import scan_dir


class SessionService:
    # ---------- Довідники ----------
    @staticmethod
    def get_analysis_methods() -> Dict[str, List[Dict[str, Any]]]:
        """
        MOCK-довідник методів аналізу (статичні дані, без БД).
        Формат повністю сумісний з моделлю MethodRegistry.
        """
        return {
            "META": [
                {
                    "id": "META_TYPE",
                    "layer": "META",
                    "domain": "GENERIC",
                    "action": "TYPE",
                    "description": "Розширення та MIME-тип файлу",
                    "returns": [
                        {"name": "real_extension", "type": "string", "unit": ""},
                        {"name": "mime_type",      "type": "string", "unit": ""}
                    ],
                    "impl_class": "methods.meta.generic.TypeExtractor",
                    "enabled": True
                },
                {
                    "id": "META_HASH_MD5",
                    "layer": "META",
                    "domain": "GENERIC",
                    "action": "HASH_MD5",
                    "description": "Контрольна сума MD5",
                    "returns": [
                        {"name": "md5", "type": "string", "unit": ""}
                    ],
                    "impl_class": "methods.meta.generic.MD5Extractor",
                    "enabled": True
                },
                {
                    "id": "META_HASH_SHA1",
                    "layer": "META",
                    "domain": "GENERIC",
                    "action": "HASH_SHA1",
                    "description": "Контрольна сума SHA-1",
                    "returns": [
                        {"name": "sha1", "type": "string", "unit": ""}
                    ],
                    "impl_class": "methods.meta.generic.SHA1Extractor",
                    "enabled": True
                },
                {
                    "id": "META_HASH_SHA256",
                    "layer": "META",
                    "domain": "GENERIC",
                    "action": "HASH_SHA256",
                    "description": "Контрольна сума SHA-256",
                    "returns": [
                        {"name": "sha256", "type": "string", "unit": ""}
                    ],
                    "impl_class": "methods.meta.generic.SHA256Extractor",
                    "enabled": True
                }
            ],
            "STRUCT": [
                {
                    "id": "IMAGE_RESOLUTION",
                    "layer": "STRUCT",
                    "domain": "IMAGE",
                    "action": "RESOLUTION",
                    "description": "Ширина та висота зображення",
                    "returns": [
                        {"name": "width",  "type": "int", "unit": "px"},
                        {"name": "height", "type": "int", "unit": "px"}
                    ],
                    "impl_class": "methods.struct.image.ImageResolutionExtractor",
                    "enabled": True
                },
                {
                    "id": "DOC_PAGECOUNT",
                    "layer": "STRUCT",
                    "domain": "DOCUMENT",
                    "action": "PAGECOUNT",
                    "description": "Кількість сторінок і слів у PDF/DOCX",
                    "returns": [
                        {"name": "page_count", "type": "int", "unit": "pages"},
                        {"name": "word_count", "type": "int", "unit": "words"}
                    ],
                    "impl_class": "methods.struct.document.DocPagecountExtractor",
                    "enabled": True
                },
                {
                    "id": "AUDIO_DURATION",
                    "layer": "STRUCT",
                    "domain": "AUDIO",
                    "action": "DURATION",
                    "description": "Тривалість і середній бітрейт аудіо",
                    "returns": [
                        {"name": "duration", "type": "float", "unit": "sec"},
                        {"name": "bitrate",  "type": "int",   "unit": "kbps"}
                    ],
                    "impl_class": "methods.struct.audio.AudioDurationExtractor",
                    "enabled": True
                }
            ],
            "CONTENT": [
                {
                    "id": "IMAGE_DESCRIBE",
                    "layer": "CONTENT",
                    "domain": "IMAGE",
                    "action": "DESCRIBE",
                    "description": "AI-генерує короткий текстовий опис зображення",
                    "returns": [
                        {"name": "description", "type": "string", "unit": ""}
                    ],
                    "impl_class": "methods.content.image.ImageDescribeExtractor",
                    "enabled": True
                },
                {
                    "id": "TEXT_NLP_SUMMARY",
                    "layer": "CONTENT",
                    "domain": "DOCUMENT",
                    "action": "SUMMARY",
                    "description": "Короткий виклад і ключові слова документа",
                    "returns": [
                        {"name": "summary",  "type": "string", "unit": ""},
                        {"name": "keywords", "type": "list",   "unit": ""}
                    ],
                    "impl_class": "methods.content.document.TextNlpSummaryExtractor",
                    "enabled": True
                },
                {
                    "id": "AUDIO_TRANSCRIPT",
                    "layer": "CONTENT",
                    "domain": "AUDIO",
                    "action": "TRANSCRIPT",
                    "description": "Транскрипція аудіо та визначення мови",
                    "returns": [
                        {"name": "transcript", "type": "string", "unit": ""},
                        {"name": "language",   "type": "string", "unit": ""}
                    ],
                    "impl_class": "methods.content.audio.AudioTranscriptExtractor",
                    "enabled": True
                }
            ]
        }
    
    @staticmethod
    def get_struct_algorithms() -> List[Dict[str, Any]]:
        """
        MOCK-версія: повертає повний список алгоритмів структурування
        у вигляді, сумісному з ORM-моделлю AlgorithmRegistry.
        """

        return [
            {
                "id": "CRITERIA",
                "description": "Групування у папки за вибраним META-полем "
                            "(тип, дата, розмір тощо). "
                            "Папка = значення або бакет поля.",
                "params_schema": {
                    "type": "object",
                    "properties": {
                        "field": {
                            "type": "string",
                            "description": "Назва поля у FileDescription "
                                        "(napр. size_bytes, mime_type, created_at)"
                        },
                        "bucket": {
                            "type": "object",
                            "description": "Опціонально — якщо поле числове/дата",
                            "properties": {
                                "type":   {"enum": ["range", "quantile"]},
                                "bounds": {"type": "array",
                                        "items": {"type": "number"}},
                                "labels": {"type": "array",
                                        "items": {"type": "string"}}
                            }
                        },
                        "rename_pattern": {
                            "type": "string",
                            "description": "Шаблон нового імені "
                                        "(наприклад {created_at:%Y-%m-%d}_{original}.{ext})"
                        }
                    },
                    "required": ["field"],
                    "additionalProperties": False
                },
                "scope": "*",  # застосовується до всієї вибірки
                "impl_class": "algorithms.criteria.CriteriaAlgorithm",
                "enabled": True
            },
            {
                "id": "CLUSTER",
                "description": "Автоматичне групування схожих файлів у кластери. "
                            "Папка = індекс кластера; назву можна змінити у прев’ю.",
                "params_schema": {
                    "type": "object",
                    "properties": {
                        "vectorizer": {
                            "enum": ["meta_tf_idf", "embedding"],
                            "default": "meta_tf_idf",
                            "description": "Спосіб перетворення описів на вектори"
                        },
                        "algo": {
                            "enum": ["kmeans", "hdbscan"],
                            "default": "kmeans",
                            "description": "Алгоритм кластеризації"
                        },
                        "k": {
                            "type": "integer",
                            "minimum": 2,
                            "default": 8,
                            "description": "Кількість кластерів (для k-means)"
                        },
                        "min_cluster": {
                            "type": "integer",
                            "minimum": 2,
                            "description": "Мінімальний розмір кластера (для HDBSCAN)"
                        }
                    },
                    "additionalProperties": False
                },
                "scope": "*",  # працює з усією вибіркою
                "impl_class": "algorithms.cluster.ClusterAlgorithm",
                "enabled": True
            }
        ]

    @staticmethod
    def get_fs_entries(dir_path: str) -> Dict[str, Any]:
        """Отримати список файлів та директорій з детальною інформацією."""
            
        # Нормалізуємо шлях
        dir_path = os.path.normpath(dir_path)

        if not dir_path.strip() or dir_path.strip() == "\\":
            return {
                "error": "Шлях не може бути порожнім або некоректним.",
                "has_access": False,
                "entries": []
            }
        
        # Визначаємо батьківську директорію
        parent_dir = os.path.dirname(dir_path)
        print(dir_path, parent_dir)
        
        if os.path.abspath(dir_path) == os.path.abspath(os.path.join(dir_path, os.pardir)):
            parent_dir = None
        
        print(dir_path, parent_dir)
        
        result = {
            "directory": dir_path,
            "parent_directory": parent_dir if dir_path != parent_dir else None,
            "entries": []
        }
        
        print(result)
        
        try:
            entries = []
            for name in os.listdir(dir_path):
                full_path = os.path.join(dir_path, name)
                
                try:
                    if os.path.isdir(full_path):
                        # Для директорій
                        entries.append({
                            "name": name,
                            "path": full_path,
                            "type": "directory",
                            "size": None,
                            "extension": None
                        })
                    else:
                        # Для файлів
                        file_size = get_file_size(full_path)
                        
                        # Отримуємо розширення (без крапки)
                        _, extension = os.path.splitext(name)
                        extension = extension.lstrip('.').lower() if extension else ""
                        
                        # Базова інформація про файл
                        file_info = {
                            "name": name,
                            "path": full_path,
                            "type": "file",
                            "size": file_size,
                            "extension": extension,  # Додаємо розширення без крапки,
                            "mime_type": get_mime_type(full_path)
                        }
                        
                        # Додаємо детальну інформацію для невеликих файлів
                        if file_size < 50 * 1024 * 1024:  # 50 MB ліміт
                            try:
                                file_info["hash"] = get_file_hash(full_path)
                                file_info["file_type"] = get_file_type(full_path)
                            except Exception as e:
                                # print(f"Файл більше 50МБ, хеш не генерується {full_path}: {e}")
                                file_info["file_type"] = get_file_type(full_path)
                        else:
                            # Для великих файлів просто додаємо тип
                            file_info["file_type"] = get_file_type(full_path)
                        entries.append(file_info)
                except Exception as e:
                    # Якщо виникла помилка при обробці файлу, додаємо базову інформацію
                    print(f"Помилка при обробці {full_path}: {e}")
                    entries.append({
                        "name": name,
                        "path": full_path,
                        "type": "unknown",
                        "extension": None,
                        "error": str(e)
                    })
            
            result["entries"] = entries
            result["has_access"] = True
            
        except PermissionError as e:
            print(f"Доступ заборонено до {dir_path}: {e}")
            result["entries"] = []
            result["has_access"] = False
            result["error"] = f"Доступ заборонено до {dir_path}: {e}"
        except Exception as e:
            # Інші помилки також обробляємо м'яко
            print(f"Помилка при отриманні списку файлів з {dir_path}: {e}")
            result["entries"] = []
            result["has_access"] = False
            result["error"] = f"Помилка: {e}"
        
        return result

    # ---------- CRUD сесій ----------
    @staticmethod
    def create_session(db: DBSession, payload: SessionCreate) -> Dict[str, Any]:
        sess = StructSession(
            directory = payload.directory,
            recursive = payload.recursive,
            status    = SessionStatus.NEW
        )
        if os.path.exists(sess.directory) and os.path.isdir(sess.directory):
            db.add(sess)
            db.commit(); db.refresh(sess)
            return {
                "id": sess.id,
                "directory": sess.directory,
                "status": sess.status
            }
        else:
            return {
                "error": f"Directory '{sess.directory}' does not exist",
                "status": "ERROR"
            }

    @staticmethod
    def list_sessions(db: DBSession, skip=0, limit=50):
        return db.query(StructSession).offset(skip).limit(limit).all()

    @staticmethod
    def get_session(db: DBSession, sid):
        return db.query(StructSession).filter(StructSession.id == sid).first()


    @staticmethod
    def analyze_and_plan(db: DBSession, sid, method_id, algorithm_id):
        sess = db.query(StructSession).filter_by(id=sid).first()
        if not sess:
            return None

        if sess.status == SessionStatus.PLANNED:
            # Повертаємо інформацію про те, що сесія вже запланована
            return {
                "already_planned": True,
                "message": f"Session {sid} is already planned. No new analysis performed."
            }

        try:
            # ---------- LOOKUP METHOD & ALGORITHM (заздалегідь) ----------
            m_rec = db.query(MethodRegistry).filter_by(id=method_id, enabled=True).first()
            if not m_rec:
                raise ValueError(f"Method '{method_id}' not found or disabled")
            MethodCls: type[MethodExtractor] = load_class(m_rec.impl_class)
            
            method_extractor = MethodCls()

            a_rec = db.query(AlgorithmRegistry).filter_by(id=algorithm_id, enabled=True).first()
            if not a_rec:
                raise ValueError(f"Algorithm '{algorithm_id}' not found or disabled")
            AlgoCls: type[StructAlgorithm] = load_class(a_rec.impl_class)
            struct_algo = AlgoCls()

            print(f"ANALYZE: {method_extractor.__class__.__name__}")
            print(f"PLAN: {struct_algo.__class__.__name__}")
            print(sess.directory, sess.recursive)
            
            # ---------- SCAN + ANALYZE (один прохід) ----------
            descriptions = []
            for meta in scan_dir(sess.directory, sess.recursive):
                print(f"ANALYZE: {meta['filename']}")
                
                # 2. обчислюємо опис методом
                dsc = method_extractor.run(meta)
                print(f"ANALYZE: {dsc}")

                # 3. накопичуємо зведений опис для планувальника
                # Додаємо повну інформацію про файл включно з шляхом
                combined_desc = {
                    **dsc,
                    "file_hash": meta.get("file_hash"),
                    "original_path": meta.get("original_path")
                }
                descriptions.append(combined_desc)
                print(combined_desc)    

            sess.files_total = len(descriptions)
            sess.analysis_method_id = method_id
            sess.status = SessionStatus.ANALYZED

            # ---------- PLAN ----------
            instr_raw = struct_algo.run(descriptions)     # MOVE/CREATE/…
            
            # Додаємо інструкції до БД
            for instr in instr_raw:
                # Використовуємо file_path замість file_hash
                file_path = instr.get("file_path", "")
                
                db.add(FileInstruction(
                    session_id=sid,
                    file_path=file_path,  # Зберігаємо повний шлях замість хешу
                    action=instr["action"],
                    status=InstructionStatus.PENDING,
                    params=instr["params"]
                ))

            sess.struct_algorithm_id = algorithm_id
            sess.actions_total = len(instr_raw)
            sess.status = SessionStatus.PLANNED
            db.commit()

            return {
                "files_analyzed": sess.files_total,
                "actions_created": sess.actions_total,
                "breakdown": {"total": sess.actions_total}
            }
            
        except Exception as e:
            db.rollback()  # Відкочуємо транзакцію у випадку помилки
            print(f"Помилка в analyze_and_plan: {str(e)}")
            # Повертаємо помилку в структурованому вигляді
            return {
                "error": str(e),
                "files_analyzed": 0,
                "actions_created": 0,
                "breakdown": {"total": 0}
            }

    # ---------- PREVIEW ----------
    @staticmethod
    def get_preview(db: DBSession, sid) -> Optional[Dict]:
        """
        Створює попередній перегляд структури файлів на основі інструкцій.
        
        Args:
            db: Сесія бази даних
            sid: ID сесії структуризації
            
        Returns:
            Optional[Dict]: Дерево структури файлів у форматі {"tree": {...}} або None
        """
        # Перевірка наявності сесії
        session = db.query(StructSession).filter_by(id=sid).first()
        if not session:
            return None
        
        # Отримуємо всі інструкції для сесії
        instructions = db.query(FileInstruction).filter_by(session_id=sid).all()
        
        # Список директорій, які потрібно створити
        directories_to_create = []
        for instr in instructions:
            if instr.action == ActionType.CREATE_DIR:
                dir_path = instr.params.get("path", "")
                if dir_path:
                    directories_to_create.append(dir_path)
        
        # Список файлів, які потрібно перемістити
        files_to_move = []
        for instr in instructions:
            if instr.action == ActionType.MOVE_FILE:
                file_path = instr.file_path
                dst_dir = instr.params.get("dst", "")
                if file_path and dst_dir:
                    files_to_move.append((file_path, dst_dir))
        
        # Створюємо дерево у потрібному форматі
        tree = {}
        
        # Додаємо всі директорії до дерева
        for dir_path in directories_to_create:
            # Розбиваємо шлях на компоненти
            parts = dir_path.strip('/\\').split('/')
            
            # Починаємо з кореневого вузла
            current_node = tree
            
            # Створюємо ієрархію директорій
            for i, part in enumerate(parts):
                if part not in current_node:
                    current_node[part] = {}
                
                # Переходимо до наступного рівня, якщо це не останній компонент
                if i < len(parts) - 1:
                    current_node = current_node[part]
        
        # Додаємо файли до дерева
        for file_path, dst_dir in files_to_move:
            # Отримуємо ім'я файлу
            file_name = os.path.basename(file_path)
            
            # Розбиваємо шлях призначення на компоненти
            dst_parts = dst_dir.strip('/\\').split('/')
            
            # Починаємо з кореневого вузла
            current_node = tree
            
            # Переходимо до цільової директорії
            for part in dst_parts:
                if part:  # Перевіряємо, що компонент не порожній
                    if part not in current_node:
                        current_node[part] = {}
                    current_node = current_node[part]
            
            # Додаємо файл з інформацією про переміщення
            current_node[file_name] = f"MOVE->{dst_dir}"
        
        return {"tree": tree}


    # ---------- APPLY ----------
    @staticmethod
    def apply_plan(db: DBSession, sid, dry_run=False) -> Optional[Dict]:
        """
        Застосовує план структуризації файлів.
        
        Args:
            db: Сесія бази даних
            sid: ID сесії структуризації
            dry_run: Якщо True, лише перевіряє можливість застосування, але не змінює систему
            
        Returns:
            Optional[Dict]: Результати застосування плану або None, якщо сесія не знайдена
        """
        sess = db.query(StructSession).filter(StructSession.id == sid).first()
        if not sess:
            return None
        
        # Базова директорія сесії
        base_directory = sess.directory
        if not base_directory:
            return {"applied": 0, "failed": 0, "errors": ["Session has no directory specified"]}

        # Отримуємо всі інструкції зі статусом PENDING
        instrs = db.query(FileInstruction).filter(
            FileInstruction.session_id == sid,
            FileInstruction.status == InstructionStatus.PENDING
        ).all()

        applied = failed = 0
        errors: List[str] = []
        
        # Множина директорій, які потрібно перевірити на порожність після переміщення файлів
        empty_dir_candidates = set()

        for instr in instrs:
            try:
                # Виконуємо дію відповідно до типу інструкції
                if instr.action == ActionType.CREATE_DIR:
                    # Створюємо директорію у базовій директорії сесії
                    dir_path = os.path.join(base_directory, instr.params.get("path", ""))
                    if not dry_run:
                        os.makedirs(dir_path, exist_ok=True)
                    instr.status = InstructionStatus.APPLIED
                    applied += 1
                    
                elif instr.action == ActionType.DELETE_EMPTY_DIR:
                    # Видаляємо порожню директорію
                    dir_path = os.path.join(base_directory, instr.params.get("path", ""))
                    if not dry_run:
                        if os.path.isdir(dir_path) and not os.listdir(dir_path):
                            os.rmdir(dir_path)
                            instr.status = InstructionStatus.APPLIED
                            applied += 1
                        else:
                            instr.status = InstructionStatus.FAILED
                            error_msg = f"Directory is not empty or does not exist: {dir_path}"
                            errors.append(error_msg)
                            failed += 1
                    
                elif instr.action == ActionType.MOVE_FILE:
                    # Переміщуємо файл
                    src_path = instr.file_path  # Повний шлях до файлу
                    src_dir = os.path.dirname(src_path)  # Директорія, з якої переміщуємо файл
                    
                    # Додаємо директорію до кандидатів на видалення
                    empty_dir_candidates.add(src_dir)
                    
                    # Цільовий шлях - базова директорія + відносний шлях
                    dst_dir = os.path.join(base_directory, instr.params.get("dst", "").rstrip("\\").rstrip("/"))
                    dst_path = os.path.join(dst_dir, os.path.basename(src_path))
                    
                    if not dry_run:
                        if os.path.exists(src_path):
                            # Переконуємося, що цільова директорія існує
                            os.makedirs(dst_dir, exist_ok=True)
                            
                            # Переміщуємо файл
                            shutil.move(src_path, dst_path)
                            instr.status = InstructionStatus.APPLIED
                            applied += 1
                        else:
                            instr.status = InstructionStatus.FAILED
                            error_msg = f"Source file does not exist: {src_path}"
                            errors.append(error_msg)
                            failed += 1
                    
                elif instr.action == ActionType.RENAME_FILE:
                    # Перейменовуємо файл
                    src_path = instr.file_path  # Повний шлях до файлу
                    src_dir = os.path.dirname(src_path)  # Директорія, з якої переміщуємо файл
                    
                    # Додаємо директорію до кандидатів на видалення
                    empty_dir_candidates.add(src_dir)
                    
                    dst_path = os.path.join(base_directory, instr.params.get("dst", ""))
                    
                    if not dry_run:
                        if os.path.exists(src_path):
                            # Переконуємося, що цільова директорія існує
                            dst_dir = os.path.dirname(dst_path)
                            os.makedirs(dst_dir, exist_ok=True)
                            
                            # Перейменовуємо файл
                            os.rename(src_path, dst_path)
                            instr.status = InstructionStatus.APPLIED
                            applied += 1
                        else:
                            instr.status = InstructionStatus.FAILED
                            error_msg = f"Source file does not exist: {src_path}"
                            errors.append(error_msg)
                            failed += 1
                
                else:
                    instr.status = InstructionStatus.FAILED
                    error_msg = f"Unknown action: {instr.action}"
                    errors.append(error_msg)
                    failed += 1
                    
            except Exception as exc:
                instr.status = InstructionStatus.FAILED
                error_msg = f"{instr.action} - {str(exc)}"
                errors.append(error_msg)
                failed += 1

        # Видаляємо порожні директорії після переміщення файлів
        if not dry_run:
            # Сортуємо директорії за довжиною шляху (щоб спочатку видаляти найглибші)
            sorted_dirs = sorted(empty_dir_candidates, key=lambda x: len(x.split(os.sep)), reverse=True)
            
            for dir_path in sorted_dirs:
                try:
                    # Перевіряємо, чи директорія існує
                    if os.path.isdir(dir_path):
                        # Перевіряємо, чи директорія порожня
                        if not os.listdir(dir_path):
                            os.rmdir(dir_path)
                            print(f"Removed empty directory: {dir_path}")
                            
                            # Додаємо батьківську директорію до кандидатів на видалення
                            parent_dir = os.path.dirname(dir_path)
                            if parent_dir and parent_dir != base_directory:
                                sorted_dirs.append(parent_dir)
                except Exception as exc:
                    print(f"Failed to remove directory {dir_path}: {str(exc)}")

        if not dry_run:
            # Оновлюємо статус сесії
            sess.status = SessionStatus.DONE if failed == 0 else SessionStatus.FAILED
            db.commit()

        return {"applied": applied, "failed": failed, "errors": errors}

    # ---------- PROGRESS ----------
    @staticmethod
    def get_progress(db: DBSession, sid) -> Optional[Dict]:
        sess = db.query(StructSession).filter(StructSession.id == sid).first()
        if not sess:
            return None

        if sess.status not in {SessionStatus.APPLYING, SessionStatus.PLANNED}:
            # якщо не в процесі – 0 або 100 %
            percent = 100 if sess.status == SessionStatus.DONE else 0
            return {"percent": percent, "status": sess.status}

        total = sess.actions_total or 1
        done = db.query(FileInstruction).filter(
            FileInstruction.session_id == sid,
            FileInstruction.status != InstructionStatus.PENDING
        ).count()
        percent = int(done / total * 100)
        return {"percent": percent, "status": sess.status}
