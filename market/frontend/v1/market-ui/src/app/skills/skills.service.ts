import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';
import { Subject } from "rxjs/internal/Subject";

export class Skill {
    id: number;
    credits: Object;
    categories: string[];
    description: string;
    icon: Object;
    icon_image: string;
    installed: boolean;
    title: string;
    summary: string;
    repository_url: string;
    triggers: string;
}

@Injectable()
export class SkillsService {
    private installUrl = '/api/install';
    private skillUrl = '/api/skill/';
    private skillsUrl = '/api/skills';
    private searchQuery = '?search=';
    public isFiltered = new Subject<boolean>();

    constructor(private http: HttpClient) { }

    getAllSkills(): Observable<Skill[]> {
        return this.http.get<Skill[]>(this.skillsUrl)
    }

    getSkillById(id: string): Observable<Skill> {
        return this.http.get<Skill>(this.skillUrl + id)
    }

    searchSkills(searchTerm: string): Observable<Skill[]> {
        this.isFiltered.next(!!searchTerm);
        return this.http.get<Skill[]>(this.skillsUrl + this.searchQuery + searchTerm)
    }

    installSkill(skill: Skill): Observable<Object> {
        return this.http.put<Object>(
            this.installUrl,
            {skill_url: skill.repository_url}
        )
    }
}
