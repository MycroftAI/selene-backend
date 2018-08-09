import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';

export class Skill {
    id: number;
    category: string;
    skill_name: string;
    title: string;
    summary: string;
    description: string;
    repository_url: string;
    triggers: string;
}

@Injectable()
export class SkillsService {
    private installUrl = '/api/install';
    private skillUrl = '/api/skill/';
    private skillsUrl = '/api/skills';
    private searchQuery = '?search=';

    constructor(private http: HttpClient) { }

    getAllSkills(): Observable<Skill[]> {
        return this.http.get<Skill[]>(this.skillsUrl)
    }

    getSkillById(id: string): Observable<Skill> {
        return this.http.get<Skill>(this.skillUrl + id)
    }

    searchSkills(searchTerm: string): Observable<Skill[]> {
        return this.http.get<Skill[]>(this.skillsUrl + this.searchQuery + searchTerm)
    }

    installSkill(): Observable<Object> {
        return this.http.get<Object>(this.installUrl)
    }
}
