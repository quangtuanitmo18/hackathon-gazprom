"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { ArrowUpDown, Search, ChevronRight } from "lucide-react";
import {
  ColumnDef, SortingState, flexRender, getCoreRowModel,
  getFilteredRowModel, getSortedRowModel, useReactTable,
} from "@tanstack/react-table";
import type { Problem } from "@/lib/api";

export function ProblemTable({ problems }: { problems: Problem[] }) {
  const [query, setQuery] = useState("");
  const [sorting, setSorting] = useState<SortingState>([{id:"problem_id",desc:false}]);
  const columns = useMemo<ColumnDef<Problem>[]>(()=>[
    { accessorKey:"problem_id", header:"Проблема",
      cell: info => <Link className="problem-link" href={`/problems/${encodeURIComponent(info.row.original.problem_id)}`}>
        <span className="problem-avatar">P</span><span><strong>{info.getValue<string>()}</strong><small>Source-scoped group</small></span><ChevronRight size={16}/></Link>
    },
    { accessorKey:"scope_id", header:"Область", cell: info=><span className="scope-tag">{info.getValue<string>()}</span> },
    { id:"ticket_count", accessorFn: row=>row.ticket_keys.length, header:"Обращений",
      cell:info=><span className="count-tag">{info.getValue<number>()}</span> },
    { accessorKey:"revision", header:"Ревизия", cell:info=><span className="muted-cell">v{info.getValue<number>()}</span> },
    { accessorKey:"status", header:"Статус",
      cell:info=><span className="status-pill"><span className="pulse-dot"/>{info.getValue<string>()==="active"?"Активна":"Объединена"}</span> },
  ],[]);
  const table=useReactTable({
    data:problems, columns, state:{sorting,globalFilter:query},
    onSortingChange:setSorting, onGlobalFilterChange:setQuery,
    getCoreRowModel:getCoreRowModel(), getFilteredRowModel:getFilteredRowModel(),getSortedRowModel:getSortedRowModel(),
    globalFilterFn:"includesString",
  });
  return (
    <div className="table-panel">
      <div className="table-tools">
        <label className="search-box"><Search size={17}/><span className="sr-only">Поиск по реестру</span>
          <input type="search" value={query} placeholder="Поиск по ID, области, статусу..."
            onChange={event=>setQuery(event.target.value)} aria-label="Поиск по реестру"/></label>
        <div className="table-subtitle">{table.getFilteredRowModel().rows.length} из {problems.length}</div>
      </div>
      <div className="table-scroll"><table>
        <thead>{table.getHeaderGroups().map(group=><tr key={group.id}>
          {group.headers.map(header=><th key={header.id}>
            {header.isPlaceholder?null:<button type="button" className="sort-button"
              onClick={header.column.getToggleSortingHandler()}
              aria-label={`Сортировать: ${typeof header.column.columnDef.header==="string"?header.column.columnDef.header:header.id}`}>
                {flexRender(header.column.columnDef.header, header.getContext())}<ArrowUpDown size={13}/>
              </button>}
          </th>)}
        </tr>)}</thead>
        <tbody>{table.getRowModel().rows.length ? table.getRowModel().rows.map(row=><tr key={row.id}>
          {row.getVisibleCells().map(cell=><td key={cell.id}>{flexRender(cell.column.columnDef.cell,cell.getContext())}</td>)}
        </tr>) : <tr><td colSpan={columns.length}><div className="empty-state">
            {problems.length ? "По вашему запросу ничего не найдено" : "Обращений пока нет. Реестр станет доступен после загрузки тикетов."}
          </div></td></tr>}</tbody>
      </table></div>
      <div className="table-footer">Только чтение · Для объединения и разделения требуется отдельная авторизация</div>
    </div>
  );
}
